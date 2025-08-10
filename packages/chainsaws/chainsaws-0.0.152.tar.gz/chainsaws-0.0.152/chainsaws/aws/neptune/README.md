# Neptune API Wrapper

AWS Neptune 그래프 데이터베이스를 위한 고수준 API 래퍼입니다.

## 개요

Neptune API 래퍼는 AWS Neptune 그래프 데이터베이스 작업을 위한 고수준 인터페이스를 제공합니다:

- 버텍스 및 엣지 작업 단순화
- 그래프 엔티티를 위한 ORM 유사 모델 정의
- Gremlin 쿼리를 위한 타입 안전 쿼리 빌더
- 트랜잭션 지원 및 연결 관리
- 포괄적인 오류 처리

## 설치

```bash
pip install chainsaws[neptune]
```

## 기본 사용법

### Neptune에 연결

```python
from chainsaws.aws.neptune import NeptuneAPI, NeptuneAPIConfig

# Neptune API 설정
config = NeptuneAPIConfig(
    port=8182,
    use_ssl=True,
    enable_iam_auth=True,
    region="us-east-1"
)

# Neptune API 초기화
neptune = NeptuneAPI(
    endpoint="your-neptune-cluster.region.neptune.amazonaws.com",
    config=config
)

# Neptune에 연결
neptune.connect()
```

### 버텍스 작업

```python
from chainsaws.aws.neptune import Vertex

# 버텍스 생성
person = Vertex(
    label="person",
    properties={
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }
)

# 버텍스 저장
person_id = neptune.create_vertex(person)
print(f"Created vertex with ID: {person_id}")

# ID로 버텍스 조회
retrieved_person = neptune.get_vertex(person_id)
print(f"Retrieved person: {retrieved_person.properties['name']}")

# 버텍스 업데이트
retrieved_person.properties["age"] = 31
neptune.update_vertex(retrieved_person)
print("Updated person's age to 31")

# 버텍스 삭제
neptune.delete_vertex(person_id)
print(f"Deleted vertex with ID: {person_id}")
```

### 엣지 작업

```python
from chainsaws.aws.neptune import Edge

# 버텍스 생성
person = Vertex(label="person", properties={"name": "John Doe"})
product = Vertex(label="product", properties={"name": "Smartphone"})

# 버텍스 저장
person_id = neptune.create_vertex(person)
product_id = neptune.create_vertex(product)

# 엣지 생성
purchased = Edge(
    label="purchased",
    from_vertex=person_id,
    to_vertex=product_id,
    properties={
        "date": "2023-05-15",
        "quantity": 1
    }
)

# 엣지 저장
edge_id = neptune.create_edge(purchased)
print(f"Created edge with ID: {edge_id}")

# ID로 엣지 조회
retrieved_edge = neptune.get_edge(edge_id)
print(f"Retrieved edge: {retrieved_edge.label}")

# 엣지 업데이트
retrieved_edge.properties["quantity"] = 2
neptune.update_edge(retrieved_edge)
print("Updated edge quantity to 2")

# 엣지 삭제
neptune.delete_edge(edge_id)
print(f"Deleted edge with ID: {edge_id}")
```

### Gremlin 쿼리 빌더 사용

```python
from chainsaws.aws.neptune import VertexQuery, EdgeQuery, CountQuery

# 버텍스 쿼리
vertex_query = VertexQuery(neptune)
people = vertex_query.V().hasLabel("person").has("age", 30).execute_vertices()
print(f"Found {len(people)} people aged 30")

# 카운트 쿼리
count_query = CountQuery(neptune)
person_count = count_query.V().hasLabel("person").count().execute()[0]
print(f"Total number of people: {person_count}")

# 복잡한 쿼리
query = EdgeQuery(neptune)
purchases = query.V().has("name", "John").outE("purchased").execute_edges()
print(f"John made {len(purchases)} purchases")
```

## 고급 사용법

더 많은 예제와 고급 사용법은 [EXAMPLES.md](EXAMPLES.md) 파일을 참조하세요. 이 파일에는 다음과 같은 내용이 포함되어 있습니다:

- 스키마 검증을 위한 커스텀 모델 정의
- 고급 쿼리 패턴 및 집계
- 경로 및 순회 쿼리
- 트랜잭션 관리
- 오류 처리

## 오류 처리

Neptune API 래퍼는 다양한 예외 유형을 제공합니다:

```python
from chainsaws.aws.neptune import (
    NeptuneError,
    NeptuneConnectionError,
    NeptuneQueryError,
    NeptuneModelError,
    NeptuneTransactionError
)

try:
    # Neptune 작업 수행
    neptune.connect()
    neptune.create_vertex(vertex)
except NeptuneConnectionError as e:
    print(f"Connection error: {e}")
except NeptuneQueryError as e:
    print(f"Query error: {e}")
except NeptuneError as e:
    print(f"General Neptune error: {e}")
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 