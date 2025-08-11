# API Gateway v2

API Gateway v2는 HTTP API와 WebSocket API를 생성하고 관리하기 위한 모듈입니다. v1(REST API)에 비해 더 간단하고 비용 효율적인 API를 구축할 수 있습니다.

## 주요 기능

- HTTP API 생성 및 관리
- WebSocket API 생성 및 관리
- Lambda 통합
- HTTP 통합
- VPC Link 통합
- JWT/Lambda 권한 부여자
- CORS 설정
- 스테이지 관리

## 사용 예시

### HTTP API 생성

```python
from chainsaws.aws.apigateway_v2 import APIGatewayV2API

# API Gateway 클라이언트 생성
api_gateway = APIGatewayV2API()

# HTTP API 생성
api = api_gateway.create_http_api(
    name="my-api",
    description="My HTTP API",
    cors_enabled=True,
    cors_origins=["https://example.com"],
    cors_methods=["GET", "POST"],
    tags={"Environment": "prod"}
)

# Lambda 통합 생성
integration = api_gateway.create_lambda_integration(
    api_id=api["ApiId"],
    lambda_arn="arn:aws:lambda:region:account:function:my-function"
)

# 라우트 생성
route = api_gateway.create_route(
    api_id=api["ApiId"],
    route_key="GET /items",
    target=integration["IntegrationId"]
)

# 스테이지 생성
stage = api_gateway.create_stage(
    api_id=api["ApiId"],
    stage_name="prod",
    auto_deploy=True
)
```

### WebSocket API 생성

```python
# WebSocket API 생성
ws_api = api_gateway.create_websocket_api(
    name="my-websocket-api",
    description="My WebSocket API",
    route_selection_expression="$request.body.action"
)

# 연결 핸들러 통합 생성
connect_integration = api_gateway.create_lambda_integration(
    api_id=ws_api["ApiId"],
    lambda_arn="arn:aws:lambda:region:account:function:connect-handler"
)

# 연결 라우트 생성
api_gateway.create_route(
    api_id=ws_api["ApiId"],
    route_key="$connect",
    target=connect_integration["IntegrationId"]
)

# 메시지 전송
api_gateway.send_websocket_message(
    api_id=ws_api["ApiId"],
    connection_id="connection-id",
    data={"message": "Hello, WebSocket!"}
)
```

### JWT 권한 부여자

```python
# Cognito JWT 권한 부여자 생성
authorizer = api_gateway.create_jwt_authorizer(
    api_id="api-id",
    name="cognito-authorizer",
    issuer="https://cognito-idp.region.amazonaws.com/user-pool-id",
    audiences=["client-id"]
)

# 보호된 라우트 생성
route = api_gateway.create_route(
    api_id="api-id",
    route_key="GET /protected",
    target="integration-id",
    authorization_type="JWT",
    authorizer_id=authorizer["AuthorizerId"]
)
```

### VPC Link 통합

```python
# VPC Link 생성
vpc_link = api_gateway.create_vpc_link(
    name="my-vpc-link",
    subnet_ids=["subnet-1234", "subnet-5678"],
    security_group_ids=["sg-1234"]
)

# VPC Link 통합 생성
integration = api_gateway.create_vpc_link_integration(
    api_id="api-id",
    vpc_link_id=vpc_link["VpcLinkId"],
    target_uri="http://internal-nlb.region.elb.amazonaws.com",
    method="POST"
)
```

## API Gateway v1 vs v2

### HTTP API (v2)의 장점
- 더 낮은 지연 시간
- 더 저렴한 비용 (REST API 대비 약 70% 저렴)
- 기본적인 API 기능에 최적화
- 간단한 CORS 설정
- JWT 권한 부여 기본 지원
- 자동 배포 지원

### REST API (v1)가 필요한 경우
- API 키가 필요한 경우
- 사용량 계획이 필요한 경우
- API 응답/요청 변환이 필요한 경우
- 프라이빗 REST API가 필요한 경우
- OpenAPI 2.0 지원이 필요한 경우

## 모범 사례

1. **보안**
   - JWT나 Lambda 권한 부여자를 사용하여 API 보호
   - VPC Link를 사용하여 프라이빗 리소스 안전하게 노출
   - CORS 설정 시 필요한 origin만 허용

2. **성능**
   - 프록시 통합 사용으로 지연 시간 최소화
   - 적절한 통합 타임아웃 설정
   - 스테이지 변수를 활용한 환경별 설정

3. **모니터링**
   - 로깅 활성화
   - 메트릭 모니터링
   - 오류 응답 추적

4. **비용 최적화**
   - HTTP API 사용 (가능한 경우)
   - 불필요한 스테이지 제거
   - 사용하지 않는 API 정리
