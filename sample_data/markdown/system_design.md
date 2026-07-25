# System Design Fundamentals

## 1. Design Principles

### SOLID Principles
| Principle | Mô tả | Ví dụ |
|-----------|-------|-------|
| **S**ingle Responsibility | Mỗi class chỉ có 1 responsibility | User class chỉ quản lý user data |
| **O**pen/Closed | Mở để extend, đóng để modify | Interface + implementations |
| **L**iskov Substitution | Subclass có thể thay thế parent | Rectangle/Square không nên kế thừa |
| **I**nterface Segregation | Nhiều interface nhỏ thay vì 1 lớn | ISP: Client không nên depend vào methods không dùng |
| **D**ependency Inversion | Depend vào abstraction, không phải concrete | Inject dependencies |

### Design Patterns

#### Creational
- **Singleton**: Đảm bảo 1 instance duy nhất
- **Factory Method**: Tạo objects mà không specify class
- **Abstract Factory**: Tạo families of related objects
- **Builder**: Tạo complex objects step by step
- **Prototype**: Clone existing objects

#### Structural
- **Adapter**: Interface compatibility
- **Decorator**: Thêm behavior dynamically
- **Facade**: Simple interface to complex subsystem
- **Proxy**: Placeholder for another object
- **Composite**: Tree structure, treat individual và composite objects like

#### Behavioral
- **Observer**: Publish-subscribe pattern
- **Strategy**: Algorithm family, make them interchangeable
- **Command**: Encapsulate request as object
- **State**: State machine behavior
- **Template Method**: Define skeleton of algorithm

## 2. Scalability

### Vertical Scaling (Scale Up)
- Thêm resources vào existing machine
- Pros: Simple, no code changes
- Cons: Limited by hardware, single point of failure

### Horizontal Scaling (Scale Out)
- Thêm nhiều machines
- Pros: Nearly unlimited scaling, fault tolerance
- Cons: Complex, need distributed systems

### Load Balancing
- **Round Robin**: Distribute equally
- **Least Connections**: Send to least busy
- **IP Hash**: Based on client IP
- **Weighted**: Based on server capacity

### Caching Strategies
- **Write-through**: Write to cache + DB simultaneously
- **Write-behind**: Write to cache, async to DB
- **Cache-aside**: Application manages cache
- **Read-through**: Cache manages DB reads

### Database Scaling
- **Read Replicas**: Multiple read-only copies
- **Sharding**: Split data across multiple DBs
- **Partitioning**: Split tables vertically/horizontally

## 3. Microservices Architecture

### Principles
- Single Responsibility per service
- Autonomous deployment
- Decentralized data management
- Fault isolation

### Communication
- **Synchronous**: REST, gRPC, GraphQL
- **Asynchronous**: Message queues (RabbitMQ, Kafka)

### Patterns
- **API Gateway**: Single entry point
- **Service Discovery**: Find services dynamically
- **Circuit Breaker**: Prevent cascade failures
- **Saga Pattern**: Distributed transactions
- **CQRS**: Separate read/write models

### Challenges
- Network latency
- Data consistency
- Service discovery
- Monitoring & debugging

## 4. System Design Interview Framework

### Step 1: Requirements Clarification
- Functional requirements
- Non-functional requirements (scalability, availability, consistency)
- Constraints

### Step 2: Back-of-envelope Estimation
- Traffic estimation
- Storage estimation
- Bandwidth estimation

### Step 3: High-Level Design
- Draw main components
- Define APIs
- Data model

### Step 4: Detailed Design
- Deep dive into components
- Algorithms
- Data structures

### Step 5: Bottlenecks & Trade-offs
- Identify bottlenecks
- Propose solutions
- Discuss trade-offs

## 5. Common Systems Design

### URL Shortener
- Generate short URL from long URL
- Redirect short URL to original
- Components: Hash function, Database, Cache

### Rate Limiter
- Limit requests per client
- Algorithms: Token Bucket, Sliding Window
- Distributed: Redis + Lua scripts

### Chat System
- Real-time messaging
- Components: WebSocket servers, Message queues, Storage
- Considerations: Message ordering, Delivery guarantees

### News Feed
- Aggregates content from followed users
- Approaches: Pull (fan-out on read), Push (fan-out on write)

### Search Autocomplete
- Typeahead suggestions
- Trie data structure
- Real-time updates

## 6. Reliability & Availability

### SLA/SLO/SLI
- **SLA**: Service Level Agreement (contract)
- **SLO**: Internal targets (99.9% uptime)
- **SLI**: Actual measurements

### Fault Tolerance
- **Redundancy**: Multiple instances
- **Replication**: Multiple copies
- **Failover**: Automatic switching
- **Graceful Degradation**: Reduced functionality

### Monitoring
- **Metrics**: CPU, memory, latency, error rates
- **Logging**: Application logs
- **Tracing**: Request flow across services
- **Alerting**: Notify on issues

## 7. Data Storage

### SQL vs NoSQL
| Feature | SQL | NoSQL |
|---------|-----|-------|
| Schema | Fixed | Flexible |
| Scaling | Vertical | Horizontal |
| Consistency | Strong | Eventual |
| Query | SQL | Various |
| Use case | Complex queries | Large scale, flexibility |

### Storage Types
- **Relational**: PostgreSQL, MySQL
- **Document**: MongoDB
- **Key-Value**: Redis, DynamoDB
- **Column-Family**: Cassandra, HBase
- **Graph**: Neo4j
- **Time-Series**: InfluxDB, TimescaleDB
