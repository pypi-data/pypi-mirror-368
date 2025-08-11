# Neptune API Examples

This document provides comprehensive examples for using the Neptune API wrapper. These examples demonstrate various functionalities and usage patterns to help you get started with the Neptune graph database.

## Table of Contents

- [Basic Usage](#basic-usage)
  - [Connecting to Neptune](#connecting-to-neptune)
  - [Vertex Operations](#vertex-operations)
  - [Edge Operations](#edge-operations)
  - [Query Builder Usage](#query-builder-usage)
- [Schema Validation](#schema-validation)
  - [Custom Vertex Models](#custom-vertex-models)
  - [Custom Edge Models](#custom-edge-models)
  - [Validation Example](#validation-example)
- [Advanced Queries](#advanced-queries)
  - [Path Traversal](#path-traversal)
  - [Aggregation Queries](#aggregation-queries)
  - [Complex Filtering](#complex-filtering)
- [Transaction Management](#transaction-management)
- [Error Handling](#error-handling)
- [Neptune vs DynamoDB](#neptune-vs-dynamodb)
  - [Data Model Comparison](#data-model-comparison)
  - [Query Patterns](#query-patterns)
  - [Type Safety](#type-safety)
  - [Best Practices](#best-practices)
- [Type-Safe Neptune Usage Examples](#type-safe-neptune-usage-examples)
  - [Strongly-Typed Property Access](#strongly-typed-property-access)
  - [Generic Query Results](#generic-query-results)
  - [Schema Validation with Pydantic](#schema-validation-with-pydantic)

## Basic Usage

### Connecting to Neptune

```python
from chainsaws.aws.neptune import NeptuneAPI, NeptuneAPIConfig

# Configure Neptune API
config = NeptuneAPIConfig(
    port=8182,
    use_ssl=True,
    enable_iam_auth=True,
    region="us-east-1"
)

# Initialize Neptune API
neptune = NeptuneAPI(
    endpoint="your-neptune-cluster.region.neptune.amazonaws.com",
    config=config
)

# Connect to Neptune
neptune.connect()
print("Successfully connected to Neptune database")
```

### Vertex Operations

```python
from chainsaws.aws.neptune import Vertex

# Create a vertex
person = Vertex(
    label="person",
    properties={
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }
)

# Save the vertex
person_id = neptune.create_vertex(person)
print(f"Created vertex with ID: {person_id}")

# Get vertex by ID
retrieved_person = neptune.get_vertex(person_id)
print(f"Retrieved person: {retrieved_person.properties['name']}")

# Update vertex
retrieved_person.properties["age"] = 31
neptune.update_vertex(retrieved_person)
print("Updated person's age to 31")

# Find vertices by property
people = neptune.find_vertices_by_property("name", "John Doe")
print(f"Found {len(people)} people named 'John Doe'")

# Delete vertex
neptune.delete_vertex(person_id)
print(f"Deleted vertex with ID: {person_id}")
```

### Edge Operations

```python
from chainsaws.aws.neptune import Edge

# Create vertices
person = Vertex(label="person", properties={"name": "John Doe"})
product = Vertex(label="product", properties={"name": "Smartphone"})

# Save vertices
person_id = neptune.create_vertex(person)
product_id = neptune.create_vertex(product)

# Create an edge
purchased = Edge(
    label="purchased",
    from_vertex=person_id,
    to_vertex=product_id,
    properties={
        "date": "2023-05-15",
        "quantity": 1
    }
)

# Save the edge
edge_id = neptune.create_edge(purchased)
print(f"Created edge with ID: {edge_id}")

# Get edge by ID
retrieved_edge = neptune.get_edge(edge_id)
print(f"Retrieved edge: {retrieved_edge.label}")

# Update edge
retrieved_edge.properties["quantity"] = 2
neptune.update_edge(retrieved_edge)
print("Updated edge quantity to 2")

# Find edges by property
purchases = neptune.find_edges_by_property("date", "2023-05-15")
print(f"Found {len(purchases)} purchases on 2023-05-15")

# Delete edge
neptune.delete_edge(edge_id)
print(f"Deleted edge with ID: {edge_id}")
```

### Query Builder Usage

```python
from chainsaws.aws.neptune import VertexQuery, EdgeQuery, CountQuery, MapQuery, ListQuery

# Vertex query
vertex_query = VertexQuery(neptune)
people = vertex_query.V().hasLabel("person").has("age", 30).execute_vertices()
print(f"Found {len(people)} people aged 30")

# Count query
count_query = CountQuery(neptune)
person_count = count_query.V().hasLabel("person").count().execute()[0]
print(f"Total number of people: {person_count}")

# Edge query
edge_query = EdgeQuery(neptune)
purchases = edge_query.V().has("name", "John").outE("purchased").execute_edges()
print(f"John made {len(purchases)} purchases")

# Map query (projection)
map_query = MapQuery(neptune)
person_details = map_query.V().hasLabel("person").project("name", "age").by("name").by("age").execute()
print(f"Person details: {person_details}")

# List query (folded results)
list_query = ListQuery(neptune)
all_ages = list_query.V().hasLabel("person").values("age").fold().execute()[0]
print(f"All ages: {all_ages}")
```

## Schema Validation

### Custom Vertex Models

You can create custom vertex models with validation logic:

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from chainsaws.aws.neptune import Vertex, NeptuneValidationError

@dataclass
class Person(Vertex):
    """Person vertex model with validation."""
    
    def __post_init__(self) -> None:
        """Validate person properties."""
        super().__post_init__()
        
        # Ensure required properties exist
        if "name" not in self.properties:
            raise NeptuneValidationError("Person must have a name")
        
        # Validate age if present
        if "age" in self.properties:
            age = self.properties["age"]
            if not isinstance(age, int) or age < 0 or age > 120:
                raise NeptuneValidationError("Age must be an integer between 0 and 120")
        
        # Set default label if not provided
        if not self.label:
            self.label = "person"
    
    @classmethod
    def create(cls, name: str, age: Optional[int] = None, email: Optional[str] = None) -> 'Person':
        """Create a person with the given properties."""
        properties: Dict[str, Any] = {"name": name}
        
        if age is not None:
            properties["age"] = age
        
        if email is not None:
            properties["email"] = email
        
        return cls(label="person", properties=properties)
```

### Custom Edge Models

Similarly, you can create custom edge models:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from chainsaws.aws.neptune import Edge, NeptuneValidationError

@dataclass
class Friendship(Edge):
    """Friendship edge model with validation."""
    
    def __post_init__(self) -> None:
        """Validate friendship properties."""
        super().__post_init__()
        
        # Set default label if not provided
        if not self.label:
            self.label = "knows"
        
        # Ensure vertices are specified
        if not self.from_vertex or not self.to_vertex:
            raise NeptuneValidationError("Friendship must have both from_vertex and to_vertex")
        
        # Add created_at timestamp if not present
        if "since" not in self.properties:
            self.properties["since"] = datetime.now().isoformat()
    
    @classmethod
    def create(cls, person1_id: str, person2_id: str, strength: Optional[int] = None) -> 'Friendship':
        """Create a friendship between two people."""
        properties = {}
        
        if strength is not None:
            if not 1 <= strength <= 10:
                raise NeptuneValidationError("Friendship strength must be between 1 and 10")
            properties["strength"] = strength
        
        return cls(
            label="knows",
            from_vertex=person1_id,
            to_vertex=person2_id,
            properties=properties
        )
```

### Validation Example

```python
def schema_validation_example():
    # Create valid person
    try:
        person = Person.create(name="John Doe", age=30, email="john@example.com")
        person_id = neptune.create_vertex(person)
        print(f"Created valid person with ID: {person_id}")
    except NeptuneValidationError as e:
        print(f"Validation error: {e}")
    
    # Try to create invalid person (age out of range)
    try:
        invalid_person = Person.create(name="Invalid", age=150)
        neptune.create_vertex(invalid_person)
    except NeptuneValidationError as e:
        print(f"Validation caught invalid age: {e}")
    
    # Create another valid person
    friend = Person.create(name="Jane Smith", age=28)
    friend_id = neptune.create_vertex(friend)
    
    # Create friendship
    try:
        friendship = Friendship.create(person_id, friend_id, strength=8)
        friendship_id = neptune.create_edge(friendship)
        print(f"Created friendship with ID: {friendship_id}")
    except NeptuneValidationError as e:
        print(f"Validation error: {e}")
```

## Advanced Queries

### Path Traversal

```python
def path_traversal_example():
    # Set up test data
    alice = neptune.create_vertex(Vertex(label="person", properties={"name": "Alice"}))
    bob = neptune.create_vertex(Vertex(label="person", properties={"name": "Bob"}))
    charlie = neptune.create_vertex(Vertex(label="person", properties={"name": "Charlie"}))
    dave = neptune.create_vertex(Vertex(label="person", properties={"name": "Dave"}))
    
    neptune.create_edge(Edge(label="knows", from_vertex=alice, to_vertex=bob))
    neptune.create_edge(Edge(label="knows", from_vertex=bob, to_vertex=charlie))
    neptune.create_edge(Edge(label="knows", from_vertex=charlie, to_vertex=dave))
    
    # Find all paths between Alice and Dave (up to 3 hops)
    paths = neptune.get_path(from_vertex_id=alice, to_vertex_id=dave, max_depth=3)
    
    print(f"Found {len(paths)} paths from Alice to Dave")
    for i, path in enumerate(paths):
        print(f"Path {i+1}:")
        for j, element in enumerate(path):
            if j % 2 == 0:  # Vertex
                print(f"  Person: {element.properties.get('name')}")
            else:  # Edge
                print(f"  --{element.label}-->")
    
    # Use query builder for custom path traversal
    from chainsaws.aws.neptune import GremlinQuery
    
    query = GremlinQuery(neptune)
    result = query.V(alice).repeat(
        query.both("knows").simplePath()
    ).until(
        query.hasId(dave).or_().loops().is_("gt(3)")
    ).hasId(dave).path().by("name").by("label").execute()
    
    print("Custom path query result:")
    for path in result:
        print(f"  {' -> '.join(str(step) for step in path)}")
```

### Aggregation Queries

```python
def aggregation_queries_example():
    # Count people by age group
    from chainsaws.aws.neptune import MapQuery
    
    age_groups = MapQuery(neptune)
    result = age_groups.V().hasLabel("person").group().by(
        age_groups.values("age").math("_ < 30 ? 'young' : (_ < 60 ? 'adult' : 'senior')")
    ).by(age_groups.count()).execute()[0]
    
    print("People by age group:")
    for group, count in result.items():
        print(f"  {group}: {count}")
    
    # Average purchase amount by product category
    avg_by_category = MapQuery(neptune)
    result = avg_by_category.V().hasLabel("product").group().by("category").by(
        avg_by_category.inE("purchased").values("amount").mean()
    ).execute()[0]
    
    print("Average purchase amount by product category:")
    for category, avg_amount in result.items():
        print(f"  {category}: ${avg_amount:.2f}")
    
    # Top 3 most connected people
    top_connected = MapQuery(neptune)
    result = top_connected.V().hasLabel("person").project("name", "connections").by("name").by(
        top_connected.both("knows").count()
    ).order().by("connections", "desc").limit(3).execute()
    
    print("Top 3 most connected people:")
    for person in result:
        print(f"  {person['name']}: {person['connections']} connections")
```

### Complex Filtering

```python
def complex_filtering_example():
    # Find people who purchased smartphones but not laptops
    from chainsaws.aws.neptune import VertexQuery
    
    smartphone_buyers = VertexQuery(neptune)
    result = smartphone_buyers.V().hasLabel("person").where(
        smartphone_buyers.outE("purchased").inV().has("category", "smartphone")
    ).where(
        smartphone_buyers.not_(
            smartphone_buyers.outE("purchased").inV().has("category", "laptop")
        )
    ).valueMap(True).execute()
    
    print("People who bought smartphones but not laptops:")
    for person in result:
        print(f"  {person.get('name', ['Unknown'])[0]}")
    
    # Find common friends between two people
    common_friends = VertexQuery(neptune)
    result = common_friends.V().has("name", "Alice").out("knows").where(
        common_friends.in_("knows").has("name", "Bob")
    ).valueMap().execute()
    
    print("Common friends between Alice and Bob:")
    for friend in result:
        print(f"  {friend.get('name', ['Unknown'])[0]}")
    
    # Find people who made purchases over $100 in the last month
    import datetime
    
    one_month_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
    
    big_spenders = VertexQuery(neptune)
    result = big_spenders.V().hasLabel("person").where(
        big_spenders.outE("purchased").has("amount", "gt(100)").has("date", "gt('" + one_month_ago + "')")
    ).valueMap().execute()
    
    print("Big spenders in the last month:")
    for person in result:
        print(f"  {person.get('name', ['Unknown'])[0]}")
```

## Transaction Management

Neptune's transaction support in Gremlin is limited, but you can use the transaction context manager to logically group operations:

```python
def transaction_example():
    try:
        # Start a transaction
        with neptune.transaction():
            # Create a person
            person = Vertex(label="person", properties={"name": "Transaction Test"})
            person_id = neptune.create_vertex(person)
            
            # Create a product
            product = Vertex(label="product", properties={"name": "Test Product"})
            product_id = neptune.create_vertex(product)
            
            # Create a purchase edge
            purchase = Edge(
                label="purchased",
                from_vertex=person_id,
                to_vertex=product_id,
                properties={"date": "2023-06-01"}
            )
            neptune.create_edge(purchase)
            
            print("All operations in transaction completed successfully")
    except Exception as e:
        print(f"Transaction failed: {e}")
        # Note: In current Neptune implementation, changes cannot be rolled back
        # and would need to be manually cleaned up
```

## Error Handling

```python
from chainsaws.aws.neptune import (
    NeptuneError,
    NeptuneConnectionError,
    NeptuneQueryError,
    NeptuneModelError,
    NeptuneTransactionError,
    NeptuneValidationError,
    NeptuneResourceNotFoundError
)

def error_handling_example():
    # Connection error
    try:
        bad_neptune = NeptuneAPI(endpoint="non-existent-cluster.neptune.amazonaws.com")
        bad_neptune.connect()
    except NeptuneConnectionError as e:
        print(f"Connection error handled: {e}")
    
    # Query error
    try:
        neptune.query("g.V().invalid()")
    except NeptuneQueryError as e:
        print(f"Query error handled: {e}")
    
    # Resource not found
    try:
        neptune.get_vertex("non-existent-id")
    except NeptuneResourceNotFoundError as e:
        print(f"Resource not found error handled: {e}")
    
    # Validation error
    try:
        invalid_vertex = Vertex(label="", properties={})  # Empty label
        neptune.create_vertex(invalid_vertex)
    except NeptuneValidationError as e:
        print(f"Validation error handled: {e}")
    
    # Model error
    try:
        # Attempting to use an unsupported model type
        class UnsupportedModel:
            pass
        
        neptune.save(UnsupportedModel())  # type: ignore
    except NeptuneModelError as e:
        print(f"Model error handled: {e}")
```

## Neptune vs DynamoDB

### Data Model Comparison

Neptune and DynamoDB are both NoSQL databases offered by AWS, but they serve different purposes and have different data models:

**Neptune (Graph Database)**:
- **Data Structure**: Stores data as vertices (nodes) and edges (relationships)
- **Model Definition**:
  ```python
  from chainsaws.aws.neptune import Vertex, Edge
  
  # Define a vertex
  person = Vertex(
      label="person",
      properties={"name": "John", "age": 30}
  )
  
  # Define an edge
  friendship = Edge(
      label="knows",
      from_vertex="person-id-1",
      to_vertex="person-id-2",
      properties={"since": "2020-01-01"}
  )
  ```
- **Strengths**: Excellent for relationship-heavy data and complex traversals
- **Use Cases**: Social networks, recommendation engines, fraud detection, knowledge graphs

**DynamoDB (Key-Value and Document Database)**:
- **Data Structure**: Stores data as items with attributes in tables with primary keys
- **Model Definition**:
  ```python
  from chainsaws.aws.dynamodb import DynamoModel
  from dataclasses import dataclass
  
  @dataclass(kw_only=True)
  class User(DynamoModel):
      _partition = "user"
      _pk = "user_id"
      _sk = "email"
      
      name: str
      email: str
      age: int
  ```
- **Strengths**: High performance, scalability, predictable latency
- **Use Cases**: User profiles, product catalogs, session management, high-throughput applications

### Query Patterns

The query patterns for these databases differ significantly:

**Neptune Queries (Gremlin)**:
```python
# Find all people John knows who are over 30
results = neptune.query("""
    g.V().has('name', 'John')
     .out('knows')
     .has('age', gt(30))
     .valueMap()
""")

# Using the fluent query builder
query = VertexQuery(neptune)
people = query.V().has('name', 'John').out('knows').has('age', gt(30)).execute_vertices()
```

**DynamoDB Queries**:
```python
# Find active users created after a certain date
results, next_key = db.query_items(
    partition="user",
    pk_field="status",
    pk_value="active",
    sk_field="created_at",
    sk_condition="gt",
    sk_value=1609459200  # Unix timestamp for 2021-01-01
)
```

### Type Safety

Both APIs provide type safety, but with different approaches:

**Neptune Type Safety**:
- Uses generic type parameters: `GremlinQuery[R]`
- Provides type aliases like `VertexQuery`, `EdgeQuery`, `CountQuery`
- Supports custom model classes that extend `Vertex` and `Edge`
- Type hints for query results and method parameters

```python
# Type-safe vertex query
from chainsaws.aws.neptune import VertexQuery, Vertex

query: VertexQuery = VertexQuery(neptune)
people: List[Vertex] = query.V().hasLabel("person").execute_vertices()

# Custom typed models
@dataclass
class Person(Vertex):
    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.label:
            self.label = "person"
    
    def get_name(self) -> Optional[str]:
        return self.properties.get("name")
    
    def get_age(self) -> Optional[int]:
        return self.properties.get("age")

# Type-safe usage
person = Person(properties={"name": "John", "age": 30})
name: Optional[str] = person.get_name()
```

**DynamoDB Type Safety**:
- Uses dataclass-based models with field type annotations
- Provides decorators like `@PK` and `@SK` for key fields
- Automatic validation of field types
- Generic type parameters for API methods

```python
from chainsaws.aws.dynamodb import DynamoModel, PK, SK
from dataclasses import dataclass

@dataclass(kw_only=True)
class User(DynamoModel):
    _partition = "user"
    
    user_id: str = PK()
    email: str = SK()
    name: str
    age: int
    
# Type-safe operations
user = User(user_id="123", email="john@example.com", name="John", age=30)
created_user: User = db.put_item("user", user)
```

### Best Practices

**Neptune Best Practices for Type Safety**:

1. **Define Custom Models**:
   ```python
   @dataclass
   class Person(Vertex):
       def __post_init__(self) -> None:
           super().__post_init__()
           if not self.label:
               self.label = "person"
       
       @classmethod
       def create(cls, name: str, age: Optional[int] = None) -> 'Person':
           properties: Dict[str, Any] = {"name": name}
           if age is not None:
               properties["age"] = age
           return cls(label="person", properties=properties)
   ```

2. **Use Type Aliases for Queries**:
   ```python
   from chainsaws.aws.neptune import VertexQuery, EdgeQuery, CountQuery
   
   def find_friends(neptune: NeptuneAPI, person_name: str) -> List[Vertex]:
       query: VertexQuery = VertexQuery(neptune)
       return query.V().has("name", person_name).out("knows").execute_vertices()
   ```

3. **Add Property Accessor Methods**:
   ```python
   @dataclass
   class Person(Vertex):
       # ... other methods ...
       
       def get_name(self) -> str:
           return str(self.properties.get("name", ""))
       
       def get_age(self) -> Optional[int]:
           age = self.properties.get("age")
           return int(age) if age is not None else None
   ```

4. **Use Type Casting for Properties**:
   ```python
   def get_property(self, key: str, default: T = None) -> Optional[T]:
       value = self.properties.get(key, default)
       if value is None:
           return None
       return cast(T, value)
   ```

5. **Create Schema Validation Utilities**:
   ```python
   def validate_vertex_schema(vertex: Vertex, required_props: List[str], 
                             type_map: Dict[str, Type]) -> bool:
       for prop in required_props:
           if prop not in vertex.properties:
               return False
       
       for prop, expected_type in type_map.items():
           if prop in vertex.properties and not isinstance(vertex.properties[prop], expected_type):
               return False
       
       return True
   ```

By following these practices, you can achieve type safety similar to DynamoDB while working with Neptune's graph data model.

## Type-Safe Neptune Usage Examples

### Strongly-Typed Property Access

One of the challenges with Neptune is that properties are stored in a dictionary, which doesn't provide type safety by default. Here's how to create strongly-typed property access:

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TypeVar, Generic, List, cast, Type
from chainsaws.aws.neptune import Vertex, Edge

T = TypeVar('T')

class PropertyAccessor(Generic[T]):
    """Type-safe property accessor."""
    
    def __init__(self, properties: Dict[str, Any], key: str, default: Optional[T] = None):
        self.properties = properties
        self.key = key
        self.default = default
    
    def get(self) -> Optional[T]:
        """Get property value with type casting."""
        value = self.properties.get(self.key, self.default)
        if value is None:
            return None
        return cast(T, value)
    
    def set(self, value: T) -> None:
        """Set property value with type checking."""
        self.properties[self.key] = value

@dataclass
class TypedPerson(Vertex):
    """Person vertex with type-safe property access."""
    
    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.label:
            self.label = "person"
    
    @property
    def name(self) -> PropertyAccessor[str]:
        return PropertyAccessor[str](self.properties, "name", "")
    
    @property
    def age(self) -> PropertyAccessor[int]:
        return PropertyAccessor[int](self.properties, "age")
    
    @property
    def active(self) -> PropertyAccessor[bool]:
        return PropertyAccessor[bool](self.properties, "active", False)
    
    @property
    def tags(self) -> PropertyAccessor[List[str]]:
        return PropertyAccessor[List[str]](self.properties, "tags", [])

# Usage example
person = TypedPerson(properties={"name": "John", "age": 30})
name: Optional[str] = person.name.get()  # Type-safe access
person.age.set(31)  # Type-safe update
tags: Optional[List[str]] = person.tags.get()  # Returns empty list as default
```

### Generic Query Results

You can use generics to create type-safe query results:

```python
from typing import TypeVar, Generic, List, Dict, Any, Optional, Type, cast
from chainsaws.aws.neptune import NeptuneAPI, GremlinQuery, Vertex, Edge

T = TypeVar('T', bound=Vertex)
E = TypeVar('E', bound=Edge)

class TypedVertexQuery(Generic[T]):
    """Type-safe vertex query."""
    
    def __init__(self, neptune: NeptuneAPI, model_class: Type[T]):
        self.neptune = neptune
        self.model_class = model_class
        self.query = GremlinQuery(neptune)
    
    def find_by_property(self, property_name: str, property_value: Any) -> List[T]:
        """Find vertices by property with type-safe results."""
        raw_vertices = self.query.V().has(property_name, property_value).execute_vertices()
        return [self.model_class.from_dict(v.to_dict()) for v in raw_vertices]
    
    def find_by_id(self, vertex_id: str) -> Optional[T]:
        """Find vertex by ID with type-safe result."""
        try:
            vertex = self.neptune.get_vertex(vertex_id)
            return self.model_class.from_dict(vertex.to_dict())
        except Exception:
            return None
    
    def find_connected(self, 
                       vertex_id: str, 
                       edge_label: str, 
                       direction: str = "out") -> List[T]:
        """Find connected vertices with type-safe results."""
        query = self.query.V(vertex_id)
        
        if direction == "out":
            query = query.out(edge_label)
        elif direction == "in":
            query = query.in_(edge_label)
        else:
            query = query.both(edge_label)
            
        raw_vertices = query.execute_vertices()
        return [self.model_class.from_dict(v.to_dict()) for v in raw_vertices]

# Define custom vertex models
@dataclass
class Person(Vertex):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        return cls(
            id=data.get("id"),
            label=data.get("label", "person"),
            properties=data.get("properties", {})
        )
    
    def get_name(self) -> str:
        return str(self.properties.get("name", ""))
    
    def get_age(self) -> Optional[int]:
        age = self.properties.get("age")
        return int(age) if age is not None else None

@dataclass
class Product(Vertex):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        return cls(
            id=data.get("id"),
            label=data.get("label", "product"),
            properties=data.get("properties", {})
        )
    
    def get_name(self) -> str:
        return str(self.properties.get("name", ""))
    
    def get_price(self) -> float:
        price = self.properties.get("price")
        return float(price) if price is not None else 0.0

# Usage example
neptune = NeptuneAPI(endpoint="your-neptune-endpoint")
person_query = TypedVertexQuery(neptune, Person)
product_query = TypedVertexQuery(neptune, Product)

# Type-safe queries
people: List[Person] = person_query.find_by_property("age", 30)
products: List[Product] = product_query.find_by_property("price", 99.99)

# Type-safe relationship traversal
person = person_query.find_by_id("person-123")
if person:
    # Get products purchased by this person
    purchased_products: List[Product] = product_query.find_connected(
        person.id, "purchased", "out"
    )
    
    for product in purchased_products:
        print(f"{person.get_name()} purchased {product.get_name()} for ${product.get_price()}")
```

### Schema Validation with Pydantic

You can use Pydantic for more robust schema validation:

```python
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from chainsaws.aws.neptune import Vertex, Edge, NeptuneAPI

# Pydantic models for property validation
class PersonProperties(BaseModel):
    name: str
    age: Optional[int] = None
    email: Optional[str] = None
    active: bool = True
    tags: List[str] = Field(default_factory=list)
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError('Age must be between 0 and 120')
        return v

class PydanticVertex(Vertex):
    """Base class for Pydantic-validated vertices."""
    
    @classmethod
    def create_with_validation(cls, label: str, properties_model: BaseModel) -> 'PydanticVertex':
        """Create a vertex with validated properties."""
        return cls(
            label=label,
            properties=properties_model.dict(exclude_none=True)
        )
    
    def update_with_validation(self, properties_model: BaseModel) -> None:
        """Update vertex properties with validation."""
        self.properties.update(properties_model.dict(exclude_none=True))

# Usage example
try:
    # Create properties with validation
    props = PersonProperties(name="John Doe", age=30, email="john@example.com")
    
    # Create vertex with validated properties
    person = PydanticVertex.create_with_validation("person", props)
    
    # Save to Neptune
    neptune = NeptuneAPI(endpoint="your-neptune-endpoint")
    neptune.create_vertex(person)
    
    # Invalid properties will raise validation error
    invalid_props = PersonProperties(name="Invalid", age=150)  # Will raise ValidationError
except Exception as e:
    print(f"Validation error: {e}")
```

These examples demonstrate how to achieve strong type safety with Neptune, making it easier to work with graph data in a type-safe manner similar to DynamoDB's approach. 