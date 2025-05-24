# TradeWise Component Architecture

## 🏗️ Component Overview

TradeWise follows a modular architecture with clear separation of concerns. Each component has specific responsibilities and well-defined interfaces.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │    Vue.js   │  │  PrimeVue   │  │   Router    │            │
│  │ Components  │  │ UI Library  │  │ Management  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ FastAPI     │  │ Middleware  │  │ WebSocket   │            │
│  │ Routers     │  │ Stack       │  │ Handlers    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Service   │  │    CRUD     │  │   Core      │            │
│  │  Classes    │  │ Operations  │  │ Utilities   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Data Access Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ SQLAlchemy  │  │   Models    │  │  Database   │            │
│  │    ORM      │  │ & Schemas   │  │ Connection  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 Frontend Components

### Vue.js Application Structure
```
frontend/vue-app/src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components (buttons, forms)
│   ├── bot/             # Bot-specific components
│   └── dashboard/       # Dashboard widgets
├── views/               # Page-level components
│   ├── auth/           # Authentication pages
│   ├── dashboard/      # Main dashboard
│   ├── bots/           # Bot management pages
│   └── marketplace/    # Bot marketplace
├── services/           # API communication
├── store/              # State management (Vuex/Pinia)
├── router/             # Route definitions
└── utils/              # Helper functions
```

### Key Frontend Components

#### Dashboard Component
```javascript
// src/components/dashboard/DashboardWidget.vue
<template>
  <div class="dashboard-widget">
    <div class="widget-header">
      <h3>{{ title }}</h3>
      <Button @click="refresh" icon="pi pi-refresh" />
    </div>
    <div class="widget-content">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardWidget',
  props: {
    title: String,
    refreshable: Boolean
  },
  methods: {
    refresh() {
      this.$emit('refresh');
    }
  }
}
</script>
```

#### Bot Connection Component
```javascript
// src/components/bot/BotConnectionForm.vue
<template>
  <form @submit.prevent="testConnection">
    <div class="field">
      <label for="apiUrl">Bot API URL</label>
      <InputText
        id="apiUrl"
        v-model="form.apiUrl"
        placeholder="http://192.168.1.100:8080"
        :class="{ 'p-invalid': errors.apiUrl }"
      />
      <small class="p-error">{{ errors.apiUrl }}</small>
    </div>
    
    <div class="field">
      <label for="apiToken">API Token</label>
      <Password
        id="apiToken"
        v-model="form.apiToken"
        :feedback="false"
        toggleMask
        :class="{ 'p-invalid': errors.apiToken }"
      />
      <small class="p-error">{{ errors.apiToken }}</small>
    </div>
    
    <Button
      type="submit"
      label="Test Connection"
      :loading="testing"
      :disabled="!isFormValid"
    />
  </form>
</template>

<script>
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import apiService from '@/services/api';

export default {
  name: 'BotConnectionForm',
  setup() {
    const toast = useToast();
    const form = ref({
      apiUrl: '',
      apiToken: ''
    });
    const errors = ref({});
    const testing = ref(false);
    
    const isFormValid = computed(() => {
      return form.value.apiUrl && form.value.apiToken;
    });
    
    const testConnection = async () => {
      testing.value = true;
      errors.value = {};
      
      try {
        const result = await apiService.testBotConnection(form.value);
        
        if (result.success) {
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Bot connection successful',
            life: 3000
          });
        } else {
          toast.add({
            severity: 'error',
            summary: 'Connection Failed',
            detail: result.message,
            life: 5000
          });
        }
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to test connection',
          life: 5000
        });
      } finally {
        testing.value = false;
      }
    };
    
    return {
      form,
      errors,
      testing,
      isFormValid,
      testConnection
    };
  }
}
</script>
```

## 🔧 Backend Components

### API Layer Structure
```
backend/app/
├── api/
│   ├── endpoints/       # Route handlers
│   │   ├── auth.py     # Authentication endpoints
│   │   ├── bots.py     # Bot management endpoints
│   │   ├── external_bots.py # External bot endpoints
│   │   └── shared_bots.py   # Shared bot endpoints
│   └── deps.py         # Dependency injection
├── core/
│   ├── config.py       # Configuration settings
│   ├── security.py     # Security utilities
│   └── logging.py      # Logging configuration
├── services/           # Business logic
├── crud/              # Database operations
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
└── middleware/        # Custom middleware
```

### Service Layer Components

#### External Bot Manager
```python
# app/services/external_bot_manager.py
class ExternalBotManager:
    """Manages connections to external trading bot instances"""
    
    def __init__(self):
        self.session = requests.Session()
        self.timeout = (5, 10)  # connect, read timeouts
        self.logger = get_logger("external_bot_manager")
    
    async def test_bot_connection(
        self, 
        api_url: str, 
        api_token: str
    ) -> BotConnectionResult:
        """Test connection to external bot with comprehensive error handling"""
        start_time = time.time()
        normalized_url = api_url.rstrip('/')
        
        try:
            # Test ping endpoint
            ping_result = await self._ping_bot(normalized_url, api_token)
            if not ping_result.success:
                return ping_result
            
            # Test status endpoint
            status_result = await self._get_bot_status(normalized_url, api_token)
            if not status_result.success:
                return status_result
            
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.info(
                "Bot connection test successful",
                extra={
                    "event_type": "bot_connection_success",
                    "api_url": normalized_url,
                    "duration_ms": duration_ms,
                    "bot_info": status_result.data
                }
            )
            
            return BotConnectionResult(
                success=True,
                message="Successfully connected to trading bot",
                data=status_result.data
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.error(
                "Bot connection test failed",
                extra={
                    "event_type": "bot_connection_error",
                    "api_url": normalized_url,
                    "duration_ms": duration_ms,
                    "error": str(e)
                },
                exc_info=True
            )
            
            return BotConnectionResult(
                success=False,
                message="Connection test failed",
                error=str(e)
            )
```

#### User Management Service
```python
# app/services/user_service.py
class UserService:
    """Handles user-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger("user_service")
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user with tenant isolation"""
        # Check if user already exists
        existing_user = crud_user.get_user_by_email(
            self.db, 
            email=user_data.email
        )
        
        if existing_user:
            self.logger.warning(
                "User registration attempt with existing email",
                extra={
                    "event_type": "user_registration_duplicate",
                    "email": user_data.email
                }
            )
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create user
        user = crud_user.create_user(self.db, user=user_data)
        
        self.logger.info(
            "New user created",
            extra={
                "event_type": "user_created",
                "user_id": str(user.id),
                "tenant_id": user.tenant_id,
                "email": user.email
            }
        )
        
        return user
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate user credentials"""
        user = crud_user.get_user_by_email(self.db, email=email)
        
        if not user or not security.verify_password(password, user.hashed_password):
            self.logger.warning(
                "Failed authentication attempt",
                extra={
                    "event_type": "authentication_failed",
                    "email": email
                }
            )
            return None
        
        if not user.is_active:
            self.logger.warning(
                "Inactive user login attempt",
                extra={
                    "event_type": "inactive_user_login",
                    "user_id": str(user.id),
                    "email": email
                }
            )
            return None
        
        self.logger.info(
            "User authenticated successfully",
            extra={
                "event_type": "authentication_success",
                "user_id": str(user.id),
                "tenant_id": user.tenant_id
            }
        )
        
        return user
```

### CRUD Layer Components

#### Bot CRUD Operations
```python
# app/crud/crud_bot.py
class BotCRUD:
    """Database operations for bot entities"""
    
    def create_bot(
        self, 
        db: Session, 
        bot_data: dict, 
        tenant_id: str
    ) -> Bot:
        """Create new bot with tenant isolation"""
        bot_data["tenant_id"] = tenant_id
        
        db_bot = Bot(**bot_data)
        db.add(db_bot)
        db.commit()
        db.refresh(db_bot)
        
        log_database_operation(
            operation="INSERT",
            table="bots",
            rows_affected=1,
            tenant_id=tenant_id
        )
        
        return db_bot
    
    def get_bots_by_tenant(
        self, 
        db: Session, 
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Bot]:
        """Get all bots for specific tenant"""
        start_time = time.time()
        
        bots = db.query(Bot)\
            .filter(Bot.tenant_id == tenant_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        duration_ms = (time.time() - start_time) * 1000
        
        log_database_operation(
            operation="SELECT",
            table="bots",
            duration_ms=duration_ms,
            rows_affected=len(bots),
            tenant_id=tenant_id
        )
        
        return bots
    
    def update_bot_status(
        self,
        db: Session,
        bot_id: str,
        tenant_id: str,
        status: str,
        connection_error: Optional[str] = None
    ) -> Optional[Bot]:
        """Update bot status with tenant verification"""
        bot = db.query(Bot)\
            .filter(
                Bot.bot_id == bot_id,
                Bot.tenant_id == tenant_id
            )\
            .first()
        
        if not bot:
            return None
        
        bot.status = status
        bot.last_ping = datetime.utcnow()
        bot.connection_error = connection_error
        bot.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(bot)
        
        log_database_operation(
            operation="UPDATE",
            table="bots",
            rows_affected=1,
            tenant_id=tenant_id,
            bot_id=bot_id,
            new_status=status
        )
        
        return bot

# Singleton instance
crud_bot = BotCRUD()
```

## 🔗 Component Interactions

### Request Flow Example
```python
# Complete flow for bot connection test
async def handle_bot_connection_test():
    # 1. API Layer - Route Handler
    @router.post("/test-connection")
    async def test_bot_connection(
        connection_test: BotConnectionTest,
        current_user: User = Depends(get_current_active_user)
    ):
        # 2. Service Layer - Business Logic
        bot_service = BotService(db)
        result = await bot_service.test_external_bot_connection(
            api_url=connection_test.api_url,
            api_token=connection_test.api_token,
            user=current_user
        )
        
        # 3. Return Response
        return result

class BotService:
    async def test_external_bot_connection(
        self,
        api_url: str,
        api_token: str,
        user: User
    ) -> dict:
        # 4. External Service Integration
        bot_manager = ExternalBotManager()
        connection_result = await bot_manager.test_bot_connection(
            api_url, api_token
        )
        
        if connection_result.success:
            # 5. Optional: Store connection test result
            await self._log_connection_test(
                user_id=user.id,
                tenant_id=user.tenant_id,
                api_url=api_url,
                result=connection_result
            )
        
        return connection_result.to_dict()
```

### Error Handling Flow
```python
# Centralized error handling across components
class TradeWiseException(Exception):
    """Base exception for TradeWise application"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None,
        details: dict = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class BotConnectionError(TradeWiseException):
    """Bot connection specific errors"""
    pass

class SecurityError(TradeWiseException):
    """Security related errors"""
    pass

# Global error handler
@app.exception_handler(TradeWiseException)
async def tradewise_exception_handler(
    request: Request, 
    exc: TradeWiseException
):
    log_security_event(
        event_type="application_error",
        description=f"Application error: {exc.message}",
        error_code=exc.error_code,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## 📦 Dependency Management

### Dependency Injection
```python
# app/api/deps.py
from fastapi import Depends
from sqlalchemy.orm import Session

# Database dependency
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Service dependencies
def get_bot_service(db: Session = Depends(get_db)) -> BotService:
    return BotService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_external_bot_manager() -> ExternalBotManager:
    return ExternalBotManager()

# Usage in endpoints
@router.post("/connect")
async def connect_external_bot(
    bot_data: ExternalBotCreate,
    current_user: User = Depends(get_current_active_user),
    bot_service: BotService = Depends(get_bot_service),
    external_bot_manager: ExternalBotManager = Depends(get_external_bot_manager)
):
    return await bot_service.connect_external_bot(
        bot_data=bot_data,
        user=current_user,
        bot_manager=external_bot_manager
    )
```

### Configuration Management
```python
# app/core/config.py
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External Services
    redis_url: str = "redis://localhost:6379/0"
    datadog_api_key: str = ""
    
    # Application
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:8080"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

This component architecture ensures maintainability, testability, and scalability while providing clear separation of concerns and well-defined interfaces between layers.