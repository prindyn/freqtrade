# TradeWise Monitoring & Observability

## 📊 Logging Architecture

### Overview
TradeWise implements structured JSON logging designed for modern observability platforms like Datadog, with comprehensive event tracking and performance monitoring.

### Logging Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Application  │    │   Logger    │    │    Logs     │    │  Datadog    │
│  Events     │    │ Middleware  │    │ Aggregator  │    │ Platform    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ API Requests     │                  │                  │
       ├─────────────────►│                  │                  │
       │ Bot Operations   │ Format as JSON   │                  │
       ├─────────────────►├─────────────────►│                  │
       │ Security Events  │ Add Metadata     │ Forward Logs     │
       ├─────────────────►├─────────────────►├─────────────────►│
       │ Business Events  │ Correlate IDs    │ Parse & Index    │
       ├─────────────────►├─────────────────►├─────────────────►│
       │ Errors/Exceptions│ Enrich Context   │ Create Metrics   │
       ├─────────────────►├─────────────────►├─────────────────►│
```

## 🔧 Logging Configuration

### JSON Log Format
```json
{
  "timestamp": "2024-01-01T12:00:00.123Z",
  "level": "INFO",
  "logger_name": "app.external_bot_manager",
  "service": "tradewise-backend",
  "environment": "production",
  "message": "Bot connection test successful",
  "event_type": "bot_connection_test_success",
  "request_id": "req-uuid-123",
  "user_id": "user-456",
  "tenant_id": "tenant-789",
  "process_id": 1234,
  "thread_id": 5678,
  "source": {
    "file": "/app/services/external_bot_manager.py",
    "line": 92,
    "function": "test_bot_connection"
  },
  "api_url": "http://192.168.1.100:8080",
  "total_duration_ms": 1250.5,
  "bot_info": {
    "state": "running",
    "trades_count": 15
  }
}
```

### Logger Setup
```python
# app/core/logging.py
import json
import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger

class DatadogJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter optimized for Datadog ingestion"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Standard fields for all logs
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        log_record['level'] = record.levelname
        log_record['logger_name'] = record.name
        log_record['service'] = 'tradewise-backend'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')
        
        # Process information
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        
        # Source code location
        log_record['source'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName
        }
        
        # Exception handling
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

def setup_logging(log_level: str = "INFO"):
    """Configure structured JSON logging"""
    formatter = DatadogJSONFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    
    # Disable uvicorn access logs (we have our own middleware)
    logging.getLogger("uvicorn.access").disabled = True
```

## 📈 Event Types & Categories

### API Events
```python
# Request/Response logging
{
  "event_type": "api_request",
  "method": "POST",
  "path": "/api/v1/external-bots/test-connection",
  "user_id": "user-123",
  "tenant_id": "tenant-456",
  "request_id": "req-789",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "query_params": {"debug": "true"}
}

{
  "event_type": "api_response",
  "method": "POST",
  "path": "/api/v1/external-bots/test-connection",
  "status_code": 200,
  "response_time_ms": 1250.5,
  "user_id": "user-123",
  "tenant_id": "tenant-456",
  "request_id": "req-789"
}
```

### Business Events
```python
# User registration
{
  "event_type": "business_user_registered",
  "user_id": "user-123",
  "tenant_id": "tenant-456",
  "email": "user@example.com",
  "client_ip": "192.168.1.100"
}

# Bot connection
{
  "event_type": "business_bot_connected",
  "user_id": "user-123",
  "tenant_id": "tenant-456",
  "bot_id": "bot-789",
  "api_url": "http://192.168.1.100:8080",
  "connection_duration_ms": 2500
}
```

### Security Events
```python
# Failed login
{
  "event_type": "security_login_failed",
  "email": "user@example.com",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "failure_reason": "invalid_credentials"
}

# Suspicious activity
{
  "event_type": "security_suspicious_activity",
  "user_id": "user-123",
  "ip_address": "192.168.1.100",
  "activity_type": "rapid_api_calls",
  "call_count": 150,
  "time_window_seconds": 60
}
```

### External API Events
```python
# Bot API calls
{
  "event_type": "external_api_call",
  "service": "trading_bot",
  "endpoint": "/api/v1/status",
  "method": "GET",
  "status_code": 200,
  "duration_ms": 850,
  "api_url": "http://192.168.1.100:8080"
}
```

### Database Events
```python
# Database operations
{
  "event_type": "database_operation",
  "operation": "SELECT",
  "table": "bots",
  "duration_ms": 25.5,
  "rows_affected": 1,
  "tenant_id": "tenant-456"
}
```

## 🎯 Key Performance Indicators (KPIs)

### Response Time Monitoring
```python
# API endpoint performance
{
  "event_type": "api_response",
  "path": "/api/v1/external-bots/test-connection",
  "response_time_ms": 1250.5,
  "p95_threshold": 2000,
  "p99_threshold": 5000,
  "performance_status": "normal"
}
```

### Bot Health Monitoring
```python
# Bot connection health
{
  "event_type": "bot_health_check",
  "bot_id": "bot-123",
  "tenant_id": "tenant-456",
  "status": "healthy",
  "response_time_ms": 500,
  "last_successful_ping": "2024-01-01T12:00:00Z",
  "consecutive_failures": 0
}
```

### Business Metrics
```python
# Daily active users
{
  "event_type": "metric_daily_active_users",
  "date": "2024-01-01",
  "active_users": 1250,
  "new_users": 45,
  "returning_users": 1205
}

# Bot usage statistics
{
  "event_type": "metric_bot_usage",
  "total_bots": 5678,
  "active_bots": 4321,
  "external_bots": 2345,
  "shared_bots": 1976,
  "avg_bots_per_user": 2.3
}
```

## 🔍 Log Correlation & Tracing

### Request Correlation
```python
# app/middleware/logging.py
import uuid

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add to all subsequent logs
        with structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                lambda _, __, event_dict: {
                    **event_dict,
                    "request_id": request_id
                }
            ]
        ):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
```

### User Journey Tracking
```python
# Track user flow through system
{
  "event_type": "user_journey_step",
  "user_id": "user-123",
  "session_id": "session-456",
  "step": "bot_connection_test",
  "step_sequence": 3,
  "previous_step": "login",
  "duration_since_last_step_ms": 30000
}
```

## 📊 Datadog Integration

### Log Forwarding Configuration
```yaml
# docker-compose.datadog.yml
version: '3.8'

services:
  datadog-agent:
    image: datadog/agent:latest
    environment:
      DD_API_KEY: ${DATADOG_API_KEY}
      DD_SITE: datadoghq.com
      DD_LOGS_ENABLED: true
      DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL: true
      DD_CONTAINER_EXCLUDE: "name:datadog-agent"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /proc/:/host/proc/:ro
      - /opt/datadog-agent/run:/opt/datadog-agent/run:rw
      - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro

  backend:
    build: ./backend
    labels:
      com.datadoghq.ad.logs: '[{
        "source": "python",
        "service": "tradewise-backend",
        "log_processing_rules": [{
          "type": "multi_line",
          "name": "log_start_with_date",
          "pattern": "\\d{4}-\\d{2}-\\d{2}"
        }]
      }]'
```

### Custom Metrics
```python
# app/monitoring/metrics.py
from datadog import DogStatsdClient

statsd = DogStatsdClient(host='localhost', port=8125)

class MetricsCollector:
    @staticmethod
    def record_api_request(endpoint: str, method: str, status_code: int, duration_ms: float):
        """Record API request metrics"""
        tags = [
            f"endpoint:{endpoint}",
            f"method:{method}",
            f"status_code:{status_code}"
        ]
        
        statsd.increment('api.requests.count', tags=tags)
        statsd.histogram('api.requests.duration', duration_ms, tags=tags)
    
    @staticmethod
    def record_bot_connection(success: bool, duration_ms: float):
        """Record bot connection metrics"""
        status = "success" if success else "failure"
        tags = [f"status:{status}"]
        
        statsd.increment('bot.connections.count', tags=tags)
        statsd.histogram('bot.connections.duration', duration_ms, tags=tags)
    
    @staticmethod
    def record_user_activity(action: str, user_id: str, tenant_id: str):
        """Record user activity metrics"""
        tags = [
            f"action:{action}",
            f"tenant_id:{tenant_id}"
        ]
        
        statsd.increment('user.activity.count', tags=tags)
```

## 📋 Log Management Best Practices

### Log Retention
```python
# Log retention policy
RETENTION_POLICIES = {
    "security_events": "2_years",
    "audit_logs": "7_years",
    "api_logs": "90_days",
    "performance_logs": "30_days",
    "debug_logs": "7_days"
}
```

### Log Sampling
```python
# High-volume endpoint sampling
class LogSampler:
    def __init__(self, sample_rate: float = 0.1):
        self.sample_rate = sample_rate
        self.always_log_events = {
            "security_",
            "business_",
            "error",
            "warning"
        }
    
    def should_log(self, event_type: str, level: str) -> bool:
        """Determine if event should be logged"""
        # Always log important events
        if any(event_type.startswith(prefix) for prefix in self.always_log_events):
            return True
        
        if level in ["ERROR", "WARNING"]:
            return True
        
        # Sample routine events
        return random.random() < self.sample_rate
```

### Sensitive Data Handling
```python
# Data sanitization
class LogSanitizer:
    SENSITIVE_FIELDS = {
        'password', 'api_token', 'secret', 'key', 
        'authorization', 'cookie', 'session'
    }
    
    @classmethod
    def sanitize(cls, data: dict) -> dict:
        """Remove or mask sensitive data from logs"""
        sanitized = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in cls.SENSITIVE_FIELDS):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize(value)
            elif isinstance(value, str) and len(value) > 100:
                # Truncate very long strings
                sanitized[key] = value[:100] + "...[truncated]"
            else:
                sanitized[key] = value
        
        return sanitized
```

## 🚨 Alerting & Monitoring

### Critical Alert Conditions
```python
# app/monitoring/alerts.py
CRITICAL_ALERTS = {
    "high_error_rate": {
        "condition": "error_rate > 5%",
        "window": "5_minutes",
        "notification": ["email", "slack", "pagerduty"]
    },
    "slow_response_time": {
        "condition": "p95_response_time > 5000ms",
        "window": "10_minutes",
        "notification": ["email", "slack"]
    },
    "database_connection_failure": {
        "condition": "db_connection_errors > 0",
        "window": "1_minute",
        "notification": ["email", "slack", "pagerduty"]
    },
    "security_breach_attempt": {
        "condition": "security_events.brute_force > 10",
        "window": "5_minutes",
        "notification": ["email", "slack", "pagerduty", "sms"]
    }
}
```

### Dashboard Queries
```sql
-- Error rate by endpoint
SELECT 
    path,
    COUNT(*) as total_requests,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
    (SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as error_rate
FROM api_logs 
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY path
ORDER BY error_rate DESC;

-- Top slow endpoints
SELECT 
    path,
    method,
    AVG(response_time_ms) as avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time
FROM api_logs 
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY path, method
ORDER BY p95_response_time DESC
LIMIT 10;

-- Bot connection success rate
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN event_type = 'bot_connection_test_success' THEN 1 ELSE 0 END) as successful,
    (SUM(CASE WHEN event_type = 'bot_connection_test_success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
FROM logs 
WHERE event_type LIKE 'bot_connection_test_%'
    AND timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

## 🔧 Development & Debugging

### Local Log Analysis
```bash
# Search for specific events
docker logs backend-container | grep "bot_connection_test" | jq '.'

# Filter by user
docker logs backend-container | jq 'select(.user_id == "user-123")'

# Monitor real-time errors
docker logs -f backend-container | jq 'select(.level == "ERROR")'

# Analyze response times
docker logs backend-container | jq 'select(.event_type == "api_response") | .response_time_ms' | sort -n
```

### Performance Analysis
```python
# app/utils/profiling.py
import time
import functools
from app.core.logging import get_logger

def profile_performance(operation_name: str):
    """Decorator to profile function performance"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger("performance")
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"Performance: {operation_name} completed",
                    extra={
                        "event_type": "performance_metric",
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "status": "success"
                    }
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Performance: {operation_name} failed",
                    extra={
                        "event_type": "performance_metric",
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error": str(e)
                    }
                )
                raise
        
        return wrapper
    return decorator

# Usage
@profile_performance("bot_connection_test")
async def test_bot_connection(api_url: str, api_token: str):
    # Function implementation
    pass
```