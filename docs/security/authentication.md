# TradeWise Security Architecture

## 🔐 Authentication & Authorization

### Overview
TradeWise implements a robust security model based on JWT tokens, multi-tenant data isolation, and comprehensive audit logging.

### Authentication Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │    │     API     │    │  Database   │    │   Logger    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Login Request │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. Validate User│                  │
       │                  ├─────────────────►│                  │
       │                  │ 3. User Data     │                  │
       │                  │◄─────────────────┤                  │
       │                  │ 4. Generate JWT  │                  │
       │                  │                  │ 5. Log Login     │
       │                  │                  ├─────────────────►│
       │ 6. JWT Token     │                  │                  │
       │◄─────────────────┤                  │                  │
       │                  │                  │                  │
       │ 7. API Request   │                  │                  │
       │    + JWT Token   │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 8. Validate JWT  │                  │
       │                  │ 9. Extract Claims│                  │
       │                  │ 10. Check Perms  │                  │
       │                  ├─────────────────►│                  │
       │                  │ 11. Execute      │                  │
       │                  │◄─────────────────┤                  │
       │ 12. Response     │                  │                  │
       │◄─────────────────┤                  │                  │
```

## 🔑 JWT Token Management

### Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",
    "tenant_id": "uuid-tenant-id",
    "user_id": 123,
    "roles": ["user"],
    "exp": 1704067200,
    "iat": 1704063600,
    "jti": "unique-token-id"
  },
  "signature": "HMACSHA256(...)"
}
```

### Token Configuration
```python
# app/core/security.py
import jwt
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict) -> str:
    """Create JWT access token with security claims"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),  # Unique token ID for revocation
        "iss": "tradewise-api",    # Issuer
        "aud": "tradewise-client"  # Audience
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            audience="tradewise-client",
            issuer="tradewise-api"
        )
        email: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        
        if email is None or tenant_id is None:
            return None
            
        return TokenData(
            email=email,
            tenant_id=tenant_id,
            user_id=payload.get("user_id"),
            roles=payload.get("roles", [])
        )
    except jwt.ExpiredSignatureError:
        log_security_event(
            event_type="token_expired",
            description="JWT token has expired"
        )
        return None
    except jwt.InvalidTokenError:
        log_security_event(
            event_type="token_invalid",
            description="Invalid JWT token"
        )
        return None
```

### Token Revocation (Future Enhancement)
```python
# Redis-based token blacklist
class TokenBlacklist:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def revoke_token(self, token_id: str, expires_at: datetime):
        """Add token to blacklist"""
        ttl = int((expires_at - datetime.utcnow()).total_seconds())
        self.redis.setex(f"blacklist:{token_id}", ttl, "revoked")
    
    def is_revoked(self, token_id: str) -> bool:
        """Check if token is revoked"""
        return self.redis.exists(f"blacklist:{token_id}")
```

## 🏢 Multi-Tenant Security

### Data Isolation
```python
# app/api/deps.py
async def get_current_active_user(
    current_user: models_user.User = Depends(get_current_user),
) -> models_user.User:
    """Get current active user with tenant context"""
    if not current_user.is_active:
        log_security_event(
            event_type="inactive_user_access",
            description="Inactive user attempted access",
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

# Tenant-aware database queries
def get_user_bots(db: Session, tenant_id: str) -> List[Bot]:
    """Get bots for specific tenant only"""
    return db.query(Bot).filter(
        Bot.tenant_id == tenant_id
    ).all()
```

### Row-Level Security (Future Enhancement)
```sql
-- Enable RLS on sensitive tables
ALTER TABLE bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Create policies for tenant isolation
CREATE POLICY tenant_isolation_bots ON bots
    FOR ALL TO app_role
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_subscriptions ON subscriptions
    FOR ALL TO app_role
    USING (
        user_id IN (
            SELECT id FROM users 
            WHERE tenant_id = current_setting('app.current_tenant_id')::uuid
        )
    );
```

## 🔒 Password Security

### Password Hashing
```python
# app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased rounds for better security
)

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

### Password Policy
```python
# app/schemas/user.py
import re
from pydantic import validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @validator('password')
    def validate_password(cls, v):
        """Enforce password complexity requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
```

## 🛡️ API Security

### Rate Limiting
```python
# app/middleware/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/auth/token")
@limiter.limit("5/minute")  # Limit login attempts
async def login_for_access_token(request: Request, ...):
    # Login logic here
    pass

@router.post("/external-bots/test-connection")
@limiter.limit("10/minute")  # Limit connection tests
async def test_bot_connection(request: Request, ...):
    # Connection test logic here
    pass
```

### Input Validation
```python
# app/schemas/bot_schemas.py
from pydantic import BaseModel, HttpUrl, validator
import re

class BotConnectionTest(BaseModel):
    api_url: str
    api_token: str

    @validator('api_url')
    def validate_api_url(cls, v):
        """Validate API URL format and restrictions"""
        # Only allow HTTP/HTTPS
        if not v.startswith(('http://', 'https://')):
            raise ValueError('API URL must use HTTP or HTTPS protocol')
        
        # Block private/internal networks in production
        if not DEBUG:
            parsed = urlparse(v)
            if parsed.hostname in ['localhost', '127.0.0.1'] or \
               parsed.hostname.startswith('192.168.') or \
               parsed.hostname.startswith('10.') or \
               parsed.hostname.startswith('172.'):
                raise ValueError('Private network URLs not allowed in production')
        
        return v

    @validator('api_token')
    def validate_api_token(cls, v):
        """Validate API token format"""
        if len(v) < 10:
            raise ValueError('API token too short')
        
        # Remove any potentially dangerous characters
        if re.search(r'[<>&"\'`;]', v):
            raise ValueError('API token contains invalid characters')
        
        return v
```

### CORS Security
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.tradewise.com",
        "https://tradewise.com"
    ] if not DEBUG else ["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)
```

## 🔐 Data Encryption

### Sensitive Data Encryption
```python
# app/core/encryption.py
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self):
        # Generate or load encryption key
        self.key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()

# Usage in models
class Bot(Base):
    # ... other fields ...
    _api_token = Column(String, name='api_token')
    
    @property
    def api_token(self) -> str:
        if self._api_token:
            return encryption.decrypt(self._api_token)
        return None
    
    @api_token.setter
    def api_token(self, value: str):
        if value:
            self._api_token = encryption.encrypt(value)
        else:
            self._api_token = None
```

## 📝 Audit Logging

### Security Event Logging
```python
# app/core/logging.py
def log_security_event(
    event_type: str,
    description: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
) -> None:
    """Log security-related events"""
    logger = get_logger("security")
    logger.warning(
        description,
        extra={
            "event_type": f"security_{event_type}",
            "user_id": user_id,
            "ip_address": ip_address,
            "severity": "high" if event_type in CRITICAL_EVENTS else "medium",
            **kwargs
        }
    )

# Critical security events that trigger alerts
CRITICAL_EVENTS = [
    "multiple_failed_logins",
    "suspicious_api_usage",
    "unauthorized_access_attempt",
    "data_exfiltration_attempt"
]
```

### Audit Trail
```python
# app/middleware/audit.py
class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capture request details
        user_id = None
        if hasattr(request.state, "user"):
            user_id = str(request.state.user.id)
        
        # Log sensitive operations
        if request.method in ["POST", "PUT", "DELETE"]:
            log_business_event(
                event_type="api_operation",
                description=f"{request.method} {request.url.path}",
                user_id=user_id,
                ip_address=request.client.host,
                method=request.method,
                path=str(request.url.path)
            )
        
        response = await call_next(request)
        return response
```

## 🚨 Incident Response

### Threat Detection
```python
# app/security/threat_detection.py
class ThreatDetector:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def detect_brute_force(self, ip_address: str, user_email: str = None):
        """Detect brute force login attempts"""
        key = f"failed_login:{ip_address}"
        if user_email:
            key += f":{user_email}"
        
        attempts = self.redis.incr(key)
        self.redis.expire(key, 300)  # 5 minute window
        
        if attempts >= 5:
            log_security_event(
                event_type="brute_force_detected",
                description="Multiple failed login attempts detected",
                ip_address=ip_address,
                email=user_email,
                attempt_count=attempts
            )
            return True
        return False
    
    def detect_suspicious_api_usage(self, user_id: str):
        """Detect unusual API usage patterns"""
        key = f"api_calls:{user_id}"
        calls = self.redis.incr(key)
        self.redis.expire(key, 60)  # 1 minute window
        
        if calls > 100:  # Threshold for suspicious activity
            log_security_event(
                event_type="suspicious_api_usage",
                description="Unusually high API usage detected",
                user_id=user_id,
                call_count=calls
            )
            return True
        return False
```

### Automated Response
```python
# app/security/automated_response.py
class SecurityAutomation:
    @staticmethod
    async def handle_security_event(event_type: str, context: dict):
        """Automated response to security events"""
        
        if event_type == "brute_force_detected":
            # Temporarily block IP
            ip_address = context.get("ip_address")
            await SecurityAutomation.block_ip(ip_address, duration=3600)
        
        elif event_type == "suspicious_api_usage":
            # Rate limit user
            user_id = context.get("user_id")
            await SecurityAutomation.rate_limit_user(user_id, duration=300)
        
        elif event_type in CRITICAL_EVENTS:
            # Send alert to security team
            await SecurityAutomation.send_security_alert(event_type, context)
    
    @staticmethod
    async def block_ip(ip_address: str, duration: int):
        """Block IP address temporarily"""
        # Implementation depends on infrastructure
        # Could update firewall rules, load balancer config, etc.
        pass
    
    @staticmethod
    async def send_security_alert(event_type: str, context: dict):
        """Send alert to security team"""
        # Send to monitoring system, email, Slack, etc.
        pass
```

## 🔍 Security Monitoring

### Metrics Collection
```python
# app/security/metrics.py
from prometheus_client import Counter, Histogram

# Security metrics
SECURITY_EVENTS = Counter(
    'security_events_total',
    'Total security events',
    ['event_type', 'severity']
)

FAILED_LOGINS = Counter(
    'failed_logins_total',
    'Total failed login attempts',
    ['ip_address']
)

AUTH_DURATION = Histogram(
    'auth_duration_seconds',
    'Authentication processing time'
)

# Usage in code
SECURITY_EVENTS.labels(event_type='brute_force', severity='high').inc()
FAILED_LOGINS.labels(ip_address=client_ip).inc()
```

### Security Dashboard Queries
```python
# Example Prometheus queries for Grafana dashboard

# Failed login rate
rate(failed_logins_total[5m])

# Security events by type
sum by (event_type) (rate(security_events_total[1h]))

# Authentication latency
histogram_quantile(0.95, auth_duration_seconds_bucket)

# Active sessions
sum(active_sessions_gauge)
```

## 📋 Security Checklist

### Development
- [ ] All passwords hashed with bcrypt (rounds ≥ 12)
- [ ] JWT tokens include all required claims
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (input sanitization)
- [ ] CSRF protection for state-changing operations

### Deployment
- [ ] HTTPS enforced for all connections
- [ ] Security headers configured (HSTS, CSP, etc.)
- [ ] Database credentials secured
- [ ] Environment variables for secrets
- [ ] Regular security updates applied
- [ ] Firewall configured properly

### Monitoring
- [ ] Audit logging enabled
- [ ] Security metrics collected
- [ ] Alerting configured for critical events
- [ ] Log retention policy defined
- [ ] Incident response procedures documented
- [ ] Regular security assessments scheduled