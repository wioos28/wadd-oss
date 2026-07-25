# Database Fundamentals

## 1. Database Types

### Relational (SQL)
- **PostgreSQL**: Advanced, open-source, extensible
- **MySQL**: Popular, fast, reliable
- **SQLite**: Embedded, serverless
- **MariaDB**: MySQL fork, community-driven
- **Oracle**: Enterprise, commercial
- **MS SQL Server**: Microsoft ecosystem

### NoSQL
| Type | DB | Use Case |
|------|-----|----------|
| Document | MongoDB, CouchDB | Content management, catalogs |
| Key-Value | Redis, DynamoDB, Memcached | Caching, sessions, real-time |
| Column-Family | Cassandra, HBase | Time-series, analytics |
| Graph | Neo4j, ArangoDB | Social networks, recommendations |
| Time-Series | InfluxDB, TimescaleDB | IoT, monitoring, metrics |

## 2. SQL Fundamentals

### DDL (Data Definition Language)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ADD COLUMN age INTEGER;
DROP TABLE users;
```

### DML (Data Manipulation Language)
```sql
INSERT INTO users (name, email) VALUES ('John', 'john@example.com');
UPDATE users SET name = 'Jane' WHERE id = 1;
DELETE FROM users WHERE id = 1;
SELECT * FROM users WHERE age > 18 ORDER BY name;
```

### Joins
```sql
-- INNER JOIN
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- FULL JOIN
SELECT u.name, o.total
FROM users u
FULL JOIN orders o ON u.id = o.user_id;
```

### Indexes
```sql
-- Single column
CREATE INDEX idx_users_email ON users(email);

-- Composite
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial
CREATE INDEX idx_active_users ON users(email) WHERE active = true;
```

## 3. Database Design

### Normalization Forms

| Form | Rule | Purpose |
|------|------|---------|
| 1NF | Atomic values, no repeating groups | Eliminate repeating groups |
| 2NF | 1NF + No partial dependencies | Eliminate partial dependencies |
| 3NF | 2NF + No transitive dependencies | Eliminate transitive dependencies |
| BCNF | 3NF + Every determinant is candidate key | Stronger 3NF |

### Denormalization
- Purpose: Improve read performance
- Trade-off: Slower writes, more storage
- When: Read-heavy workloads, analytics

## 4. Transactions

### ACID Properties
| Property | Mô tả |
|----------|-------|
| **Atomicity** | All or nothing |
| **Consistency** | Valid state transitions |
| **Isolation** | Concurrent transactions don't interfere |
| **Durability** | Committed data survives crashes |

### Isolation Levels
| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|------------|---------------------|--------------|
| Read Uncommitted | Yes | Yes | Yes |
| Read Committed | No | Yes | Yes |
| Repeatable Read | No | No | Yes |
| Serializable | No | No | No |

## 5. Query Optimization

### EXPLAIN ANALYZE
```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'john@example.com';
```

### Common Optimizations
1. **Add Indexes**: On frequently queried columns
2. **Avoid SELECT ***: Select only needed columns
3. **Use LIMIT**: For large result sets
4. **Optimize Joins**: Use proper join types
5. **Batch Inserts**: Reduce round trips
6. **Connection Pooling**: Reuse connections

## 6. Scaling Patterns

### Read Replicas
- Multiple read-only copies
- Primary handles writes
- Replicas handle reads
- Eventual consistency

### Sharding
- Split data across multiple databases
- Shard key determines placement
- Horizontal scaling
- Complex queries across shards

### Connection Pooling
- Reuse database connections
- Reduce overhead
- Tools: PgBouncer, ProxySQL

## 7. Backup & Recovery

### Backup Types
- **Full**: Complete database
- **Incremental**: Changes since last backup
- **Differential**: Changes since last full backup

### Recovery Strategies
- Point-in-time recovery
- Disaster recovery
- High availability (HA)
