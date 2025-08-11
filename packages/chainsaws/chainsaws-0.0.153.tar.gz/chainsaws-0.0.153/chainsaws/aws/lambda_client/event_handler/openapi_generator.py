"""Module for OpenAPI specification generation and schema management"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Type, TypedDict, ClassVar, get_type_hints, Callable
from dataclasses import is_dataclass, fields

from chainsaws.aws.lambda_client.event_handler.handler_models import OpenAPIRoute

logger = logging.getLogger(__name__)

DEFAULT_REGION = "ap-northeast-2"


class OpenAPIConfigDict(TypedDict, total=False):
    """OpenAPI configuration"""
    title: str
    version: str
    description: str
    servers: List[Dict[str, str]]
    tags: List[Dict[str, str]]
    s3_bucket: Optional[str]  # S3 bucket for schema storage
    s3_key: Optional[str]  # S3 key for schema storage


def is_build_time() -> bool:
    """Detect if current execution is at build time"""
    # 1. Explicit environment variable check
    if os.getenv("CHAINSAWS_BUILD_TIME") == "1":
        return True

    # 2. Detect pytest execution
    if "pytest" in sys.modules:
        return True

    # 3. Detect mypy execution
    if any("mypy" in arg for arg in sys.argv):
        return True

    # 4. Detect pyright execution
    if any("pyright" in arg for arg in sys.argv):
        return True

    # 5. Detect CI/CD environment
    # These are common CI environment variables
    ci_env_vars = [
        "CI",                    # Generic CI
        "GITHUB_ACTIONS",        # GitHub Actions
        "GITLAB_CI",            # GitLab CI
        "JENKINS_URL",          # Jenkins
        "TRAVIS",               # Travis CI
        "CIRCLECI",            # Circle CI
        "BITBUCKET_BUILD_NUMBER",  # Bitbucket Pipelines
        "TEAMCITY_VERSION",     # TeamCity
        "BAMBOO_BUILD_NUMBER",  # Bamboo
        "CODEBUILD_BUILD_ID",   # AWS CodeBuild
        "BUILD_ID",             # Generic build ID
        "BUILD_NUMBER"          # Generic build number
    ]

    if any(os.getenv(var) for var in ci_env_vars):
        return True

    return False


IS_BUILD_TIME = is_build_time()


class OpenAPIGenerator:
    """OpenAPI specification generator"""

    def __init__(self, config: Optional[OpenAPIConfigDict] = None):
        self.config = config or {
            "title": "API Documentation",
            "version": "1.0.0",
            "description": "",
            "servers": [],
            "tags": []
        }

    def get_docs_url(self) -> Optional[str]:
        """Get S3 website URL for documentation"""
        s3_bucket = self.config.get("s3_bucket")
        if not s3_bucket:
            return None
        region = os.environ.get("AWS_REGION", DEFAULT_REGION)
        return f"http://{s3_bucket}.s3-website-{region}.amazonaws.com"

    def _get_redoc_html(self, spec_url: str) -> str:
        return f'''
<!DOCTYPE html>
<html>
  <head>
    <title>{self.config["title"]}</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
  </head>
  <body>
    <redoc spec-url="{spec_url}"></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
'''

    def generate_spec(self, routes: Dict[str, List[OpenAPIRoute]]) -> dict:
        """Generate OpenAPI specification"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.config["title"],
                "version": self.config["version"],
                "description": self.config["description"]
            },
            "servers": self.config["servers"],
            "tags": self.config["tags"],
            "paths": {}
        }

        for method, route_list in routes.items():
            for route in route_list:
                path_spec = self._generate_path_spec(route)
                if route.path not in spec["paths"]:
                    spec["paths"][route.path] = {}
                spec["paths"][route.path][method.lower()] = path_spec

        return spec

    def _generate_path_spec(self, route: OpenAPIRoute) -> dict:
        """Generate path specification for a route"""
        metadata = route.openapi_metadata
        spec = {
            "summary": metadata.get("summary", ""),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "parameters": self._get_path_parameters(route),
            "responses": metadata.get("responses", {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {}
                        }
                    }
                }
            })
        }

        # Add CORS headers
        if route.cors:
            if "options" not in spec:
                spec["options"] = {}
            spec["options"]["responses"] = {
                "200": {
                    "description": "CORS preflight response",
                    "headers": {
                        "Access-Control-Allow-Origin": {
                            "schema": {"type": "string"}
                        },
                        "Access-Control-Allow-Methods": {
                            "schema": {"type": "string"}
                        },
                        "Access-Control-Allow-Headers": {
                            "schema": {"type": "string"}
                        }
                    }
                }
            }

        return spec

    def _get_path_parameters(self, route: OpenAPIRoute) -> List[dict]:
        """Extract path parameters from route"""
        params = []
        if not route.is_static and route._pattern:
            for param_name in route._pattern.groupindex:
                params.append({
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                })
        return params


class ResponseSchemaRegistry:
    """Registry for response schemas at build time"""
    _schemas: ClassVar[Dict[str, dict]] = {}
    _config: ClassVar[OpenAPIConfigDict] = {
        "title": "API Documentation",
        "version": "1.0.0",
        "description": "",
        "servers": [],
        "tags": [],
        "s3_bucket": os.getenv("CHAINSAWS_SCHEMA_S3_BUCKET"),
        "s3_key": os.getenv("CHAINSAWS_SCHEMA_S3_KEY", "openapi.json")
    }

    @classmethod
    def configure(cls, config: OpenAPIConfigDict) -> None:
        """Configure the registry"""
        cls._config.update(config)

    @classmethod
    def register(cls, model_name: str, schema: dict) -> None:
        """Register schema at build time only"""
        if IS_BUILD_TIME:
            cls._schemas[model_name] = schema
            cls.save_schemas()

    @classmethod
    def save_schemas(cls) -> None:
        """Upload schemas and documentation to S3"""
        if not IS_BUILD_TIME:
            return

        s3_bucket = cls._config.get("s3_bucket")
        if not s3_bucket:
            return

        try:
            from chainsaws.aws.s3 import S3API
            s3 = S3API(bucket_name=s3_bucket)

            # 1. Enable website hosting
            s3.init_s3_bucket(website=True)

            # 2. Upload OpenAPI spec
            def schema_generator():
                yield b'{\n'
                for i, (key, value) in enumerate(cls._schemas.items()):
                    chunk = json.dumps({key: value}, indent=2)[
                        1:-1].encode('utf-8')
                    if i > 0:
                        yield b',\n'
                    yield chunk
                yield b'\n}'

            s3.upload_large_file(
                object_key="openapi.json",
                file_bytes=schema_generator(),
                content_type="application/json",
                part_size=5 * 1024 * 1024
            )

            # 3. Upload ReDoc HTML
            generator = OpenAPIGenerator(cls._config)
            html_content = generator._get_redoc_html("openapi.json")
            s3.put_object(
                object_key="docs",
                body=html_content.encode('utf-8'),
                content_type="text/html"
            )

            region = os.environ.get("AWS_REGION", DEFAULT_REGION)
            logger.info(
                f"Documentation uploaded to http://{s3_bucket}.s3-website-{region}.amazonaws.com/docs")
        except Exception as e:
            logger.warning(f"Failed to upload documentation to S3: {e}")

    @classmethod
    def load_schemas(cls) -> Dict[str, dict]:
        """Load schemas from S3 using streaming at runtime"""
        if IS_BUILD_TIME:
            return cls._schemas

        s3_bucket = cls._config.get("s3_bucket")
        s3_key = cls._config.get("s3_key", "openapi.json")

        if s3_bucket:
            try:
                from chainsaws.aws.s3.s3 import S3API
                s3 = S3API(bucket_name=s3_bucket)

                # Stream reading
                schemas = {}
                # 1MB chunks
                for chunk in s3.stream_object(object_key=s3_key, chunk_size=1024 * 1024):
                    # Parse chunks and merge into schemas dictionary
                    try:
                        chunk_data = json.loads(chunk.decode('utf-8'))
                        schemas.update(chunk_data)
                    except json.JSONDecodeError:
                        # Skip incomplete JSON chunks
                        continue
                return schemas
            except Exception as e:
                logger.warning(f"Failed to load schema from S3: {e}")

        return cls._schemas


def create_schema_from_type(typ: Type) -> Optional[dict]:
    """Generate OpenAPI schema from type (build time only)"""
    if not IS_BUILD_TIME:
        return None

    if is_dataclass(typ):
        properties = {}
        required = []
        for field in fields(typ):
            field_schema = create_schema_from_type(field.type)
            if field_schema:
                properties[field.name] = field_schema
                if field.default == field.default_factory:
                    required.append(field.name)
        schema = {
            "type": "object",
            "properties": properties
        }
        if required:
            schema["required"] = required
        return schema
    elif hasattr(typ, '__origin__'):
        if typ.__origin__ is list:
            item_schema = create_schema_from_type(typ.__args__[0])
            if item_schema:
                return {
                    "type": "array",
                    "items": item_schema
                }
        elif typ.__origin__ is dict:
            value_schema = create_schema_from_type(typ.__args__[1])
            if value_schema:
                return {
                    "type": "object",
                    "additionalProperties": value_schema
                }
    elif isinstance(typ, type):
        if issubclass(typ, str):
            return {"type": "string"}
        elif issubclass(typ, int):
            return {"type": "integer"}
        elif issubclass(typ, float):
            return {"type": "number"}
        elif issubclass(typ, bool):
            return {"type": "boolean"}
    return None


def response_model(cls: Type) -> Type:
    """Decorator to generate OpenAPI schema for response model at build time"""
    if IS_BUILD_TIME:
        schema = create_schema_from_type(cls)
        if schema:
            setattr(cls, '__response_schema__', schema)
            ResponseSchemaRegistry.register(
                f"{cls.__module__}.{cls.__name__}", schema)
    return cls


def response(status_code: int = 200, description: str = "") -> Callable:
    """Decorator to specify response model"""
    def decorator(func: Callable) -> Callable:
        if IS_BUILD_TIME:
            response_type = get_type_hints(func).get('return')
            if response_type and hasattr(response_type, '__response_schema__'):
                schema = getattr(response_type, '__response_schema__')
                response_schema = {
                    str(status_code): {
                        "description": description or "Successful response",
                        "content": {
                            "application/json": {
                                "schema": schema
                            }
                        }
                    }
                }
                setattr(func, '__response_schema__', response_schema)
                ResponseSchemaRegistry.register(
                    f"{func.__module__}.{func.__name__}",
                    response_schema
                )
        return func
    return decorator
