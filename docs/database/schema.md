# TradeWise Database Design

## 🗃️ Database Schema

### Overview
TradeWise uses PostgreSQL as the primary database with a multi-tenant architecture. Each tenant's data is isolated using a `tenant_id` field across all tables.

## 📊 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Users       │       │      Bots       │       │  Bot_Templates  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │   ┌───│ id (PK)         │       │ id (PK)         │
│ email           │   │   │ bot_id          │       │ template_id     │
│ hashed_password │   │   │ tenant_id (FK)  │───────│ name            │
│ full_name       │   │   │ bot_type        │       │ description     │
│ is_active       │   │   │ name            │       │ config_json     │
│ tenant_id       │───┘   │ description     │       │ is_public       │
│ created_at      │       │ status          │       │ risk_level      │
│ updated_at      │       │ api_url         │       │ strategy_type   │
└─────────────────┘       │ api_token       │       │ created_at      │
                          │ config_template │───────│ updated_at      │
                          │ is_public       │       └─────────────────┘
                          │ exposed_port    │
                          │ last_ping       │       ┌─────────────────┐
                          │ connection_error│       │ Subscriptions   │
                          │ created_at      │       ├─────────────────┤
                          │ updated_at      │       │ id (PK)         │
                          └─────────────────┘       │ user_id (FK)    │
                                    │               │ bot_id (FK)     │
                                    └───────────────│ template_id(FK) │
                                                    │ allocation_amt  │
                                                    │ status          │
                                                    │ created_at      │
                                                    │ updated_at      │
                                                    └─────────────────┘
```

## 📋 Table Definitions

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

**Description:** Stores user authentication and profile information. Each user gets a unique `tenant_id` for data isolation.

### Bots Table
```sql
CREATE TABLE bots (
    id SERIAL PRIMARY KEY,
    bot_id VARCHAR(255) UNIQUE NOT NULL,
    tenant_id UUID NOT NULL,
    bot_type VARCHAR(50) NOT NULL, -- 'external', 'shared', 'platform'
    name VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'inactive', -- 'inactive', 'starting', 'running', 'stopping', 'error', 'connected'
    
    -- External bot fields
    api_url VARCHAR(512),
    api_token VARCHAR(512),
    
    -- Shared/Platform bot fields
    config_template VARCHAR(255),
    is_public BOOLEAN DEFAULT FALSE,
    exposed_host_port INTEGER,
    
    -- Health monitoring
    last_ping TIMESTAMP,
    connection_error TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (tenant_id) REFERENCES users(tenant_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_bots_tenant_id ON bots(tenant_id);
CREATE INDEX idx_bots_bot_id ON bots(bot_id);
CREATE INDEX idx_bots_type ON bots(bot_type);
CREATE INDEX idx_bots_status ON bots(status);
CREATE INDEX idx_bots_public ON bots(is_public) WHERE is_public = TRUE;

-- Ensure unique bot URLs per tenant for external bots
CREATE UNIQUE INDEX idx_bots_unique_external_url 
ON bots(tenant_id, api_url) 
WHERE bot_type = 'external' AND api_url IS NOT NULL;
```

**Description:** Central table for all bot instances. Supports multiple bot types with type-specific fields.

### Bot_Templates Table
```sql
CREATE TABLE bot_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config_json JSONB NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    strategy_type VARCHAR(50), -- 'dca', 'grid', 'momentum', 'arbitrage'
    performance_data JSONB, -- Store historical performance metrics
    creator_tenant_id UUID,
    subscribers_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (creator_tenant_id) REFERENCES users(tenant_id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_templates_public ON bot_templates(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_templates_risk ON bot_templates(risk_level);
CREATE INDEX idx_templates_strategy ON bot_templates(strategy_type);
CREATE INDEX idx_templates_creator ON bot_templates(creator_tenant_id);

-- GIN index for JSONB performance data queries
CREATE INDEX idx_templates_performance ON bot_templates USING GIN (performance_data);
CREATE INDEX idx_templates_config ON bot_templates USING GIN (config_json);
```

**Description:** Templates for shared bot strategies. Contains configuration and performance data.

### Subscriptions Table
```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    bot_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    allocation_amount DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'paused', 'cancelled'
    performance_data JSONB, -- User-specific performance tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES bot_templates(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_bot ON subscriptions(bot_id);
CREATE INDEX idx_subscriptions_template ON subscriptions(template_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- Ensure one subscription per user per template
CREATE UNIQUE INDEX idx_subscriptions_unique 
ON subscriptions(user_id, template_id) 
WHERE status = 'active';
```

**Description:** Tracks user subscriptions to shared bot templates.

### Audit_Logs Table (Future)
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

**Description:** Complete audit trail of all user actions for compliance and debugging.

## 🔐 Data Security

### Encryption
- **API Tokens**: Encrypted using AES-256 before storage
- **Sensitive Config**: Bot configurations encrypted in JSONB fields
- **Connection Strings**: Database connection credentials encrypted

### Data Isolation
- **Tenant ID**: Every data access filtered by `tenant_id`
- **Row Level Security**: PostgreSQL RLS policies for additional protection
- **API Level**: Application enforces tenant isolation

## 📈 Performance Considerations

### Indexing Strategy
- **Primary Keys**: Auto-incrementing integers for fast joins
- **Foreign Keys**: All foreign key columns indexed
- **Query Patterns**: Indexes designed for common query patterns
- **JSONB Fields**: GIN indexes for flexible JSON queries

### Connection Pooling
```python
# Database connection configuration
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600
}
```

### Query Optimization
- **Prepared Statements**: SQLAlchemy ORM with query caching
- **Batch Operations**: Bulk inserts/updates for large datasets
- **Read Replicas**: Future scaling with read-only replicas

## 🔄 Migration Strategy

### Schema Versioning
```python
# Alembic migration example
def upgrade():
    # Add new columns with defaults
    op.add_column('bots', sa.Column('last_ping', sa.TIMESTAMP()))
    op.add_column('bots', sa.Column('connection_error', sa.TEXT()))
    
    # Create indexes
    op.create_index('idx_bots_last_ping', 'bots', ['last_ping'])

def downgrade():
    # Reverse operations
    op.drop_index('idx_bots_last_ping')
    op.drop_column('bots', 'connection_error')
    op.drop_column('bots', 'last_ping')
```

### Data Migration
- **Backwards Compatible**: New columns with sensible defaults
- **Zero Downtime**: Rolling deployments with compatible schemas
- **Rollback Plan**: Every migration includes downgrade path

## 📊 Monitoring & Analytics

### Performance Metrics
```sql
-- Query performance monitoring
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE schemaname = 'public';

-- Index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public';
```

### Data Growth Tracking
```sql
-- Table size monitoring
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🚀 Scaling Considerations

### Horizontal Scaling
- **Read Replicas**: Scale read operations across multiple nodes
- **Sharding**: Future partitioning by tenant_id if needed
- **Connection Pooling**: PgBouncer for connection management

### Vertical Scaling
- **Memory**: Increase shared_buffers and work_mem
- **Storage**: Fast SSD storage for optimal I/O
- **CPU**: Scale processing power for complex queries

### Backup Strategy
- **Point-in-Time Recovery**: Continuous WAL archiving
- **Daily Snapshots**: Full database backups
- **Cross-Region**: Backup replication for disaster recovery