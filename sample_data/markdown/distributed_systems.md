# Distributed Systems

## 1. Fundamentals

### CAP Theorem
Không thể đạt được cả 3 cùng lúc:
- **Consistency**: Mọi node thấy data giống nhau
- **Availability**: Mọi request đều được response
- **Partition Tolerance**: Hệ thống hoạt động khi network partition

Chọn 2:
- **CP**: Consistent + Partition tolerant (databases)
- **AP**: Available + Partition tolerant (cassandra, dynamodb)

### PACELC Theorem
Extension của CAP:
- Nếu Partition: Choose Availability hoặc Consistency
- Else: Choose Latency hoặc Consistency

## 2. Consistency Models

| Model | Mô tả | Use Case |
|-------|-------|----------|
| Strong | Write immediately visible everywhere | Banking |
| Eventual | Eventually consistent | Social media |
| Causal | Causal ordering preserved | Collaborative editing |
| Linearizable | Serial execution order | Strong consistency |

## 3. Distributed Consensus

### Raft
- Leader election
- Log replication
- Safety guarantees

### Paxos
- Complex but proven
- Used in: Chubby, Spanner

### ZAB (ZooKeeper Atomic Broadcast)
- Used in: ZooKeeper
- Primary-backup replication

## 4. Data Distribution

### Sharding Strategies
- **Hash-based**: Consistent hashing
- **Range-based**: Key ranges
- **Geographic**: Location-based

### Replication
- **Leader-Follower**: One primary, multiple replicas
- **Multi-leader**: Multiple primaries
- **Leaderless**: Dynamo-style

### Consistency Protocols
- **2PC (Two-Phase Commit)**: Coordinator-based
- **3PC**: Improved 2PC
- **Saga**: Long-running transactions
- **TCC**: Try-Confirm-Cancel

## 5. Distributed Transactions

### Saga Pattern
```
T1 → T2 → T3 → T4
|    |    |    |
C1 ← C2 ← C3 ← C4 (Compensating transactions)
```

### Event Sourcing
- Store events, not state
- Rebuild state from events
- Audit trail built-in

### CQRS (Command Query Responsibility Segregation)
- Separate read/write models
- Different databases for each
- Eventual consistency

## 6. Distributed Caching

### Redis Cluster
- Hash slots
- Automatic sharding
- Failover

### Memcached
- Simple key-value
- Multi-threaded
- No persistence

### Cache Strategies
- **Write-through**: Sync write to cache + DB
- **Write-behind**: Async write to DB
- **Cache-aside**: App manages cache
- **Read-through**: Cache manages DB

## 7. Message Queues

### Patterns
- **Point-to-Point**: One producer, one consumer
- **Publish-Subscribe**: One producer, many consumers
- **Request-Reply**: Synchronous over async

### Tools
- **RabbitMQ**: AMQP, flexible routing
- **Apache Kafka**: High throughput, event streaming
- **Amazon SQS**: Managed, scalable
- **NATS**: Lightweight, fast

## 8. Service Mesh

### Components
- **Data Plane**: Sidecar proxies
- **Control Plane**: Configuration management

### Features
- Traffic management
- Security (mTLS)
- Observability
- Resilience

### Tools
- **Istio**: Feature-rich
- **Linkerd**: Lightweight
- **Consul Connect**: HashiCorp

## 9. Distributed Storage

### Key-Value
- **DynamoDB**: AWS managed
- **Cassandra**: Wide-column store
- **Riak**: AP system

### Object Storage
- **S3**: AWS standard
- **MinIO**: Self-hosted S3-compatible

### Distributed SQL
- **CockroachDB**: Postgres-compatible
- **TiDB**: MySQL-compatible
- **Spanner**: Google's globally distributed DB

## 10. Observability

### Metrics
- **Prometheus**: Time-series metrics
- **StatsD**: Simple metrics

### Logging
- **ELK Stack**: Elasticsearch + Logstash + Kibana
- **Loki**: Log aggregation

### Tracing
- **Jaeger**: Open-source tracing
- **Zipkin**: Distributed tracing
- **OpenTelemetry**: Vendor-neutral
