from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class ExternalBotCreate(BaseModel):
    """Schema for connecting to an external FreqTrade bot"""
    name: str
    description: Optional[str] = None
    api_url: str  # e.g., "http://192.168.1.100:8080"
    auth_method: Literal["token", "basic"] = "token"
    
    # Token authentication fields
    api_token: Optional[str] = None
    
    # Basic authentication fields
    username: Optional[str] = None
    password: Optional[str] = None
    
    @validator('api_token')
    def validate_token_auth(cls, v, values):
        if values.get('auth_method') == 'token' and not v:
            raise ValueError('api_token is required when auth_method is token')
        return v
    
    @validator('username')
    def validate_basic_auth_username(cls, v, values):
        if values.get('auth_method') == 'basic' and not v:
            raise ValueError('username is required when auth_method is basic')
        return v
    
    @validator('password')
    def validate_basic_auth_password(cls, v, values):
        if values.get('auth_method') == 'basic' and not v:
            raise ValueError('password is required when auth_method is basic')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "My Trading Bot",
                "description": "BTC/ETH trading bot on my home server",
                "api_url": "http://192.168.1.100:8080",
                "auth_method": "token",
                "api_token": "your-bot-api-token-here"
            }
        }


class SharedBotCreate(BaseModel):
    """Schema for creating a shared platform bot"""
    name: str
    description: str
    config_template: str  # Name/ID of the configuration template
    is_public: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Conservative BTC Strategy",
                "description": "Low-risk DCA strategy for BTC/USDT",
                "config_template": "conservative_btc_v1",
                "is_public": True
            }
        }


class BotConnectionTest(BaseModel):
    """Schema for testing bot connection"""
    api_url: str
    auth_method: Literal["token", "basic"] = "token"
    api_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    @validator('api_token')
    def validate_token_auth(cls, v, values):
        if values.get('auth_method') == 'token' and not v:
            raise ValueError('api_token is required when auth_method is token')
        return v
    
    @validator('username')
    def validate_basic_auth_username(cls, v, values):
        if values.get('auth_method') == 'basic' and not v:
            raise ValueError('username is required when auth_method is basic')
        return v
    
    @validator('password')
    def validate_basic_auth_password(cls, v, values):
        if values.get('auth_method') == 'basic' and not v:
            raise ValueError('password is required when auth_method is basic')
        return v


class BotResponse(BaseModel):
    """Enhanced bot response schema"""
    id: int
    bot_id: str
    tenant_id: str
    bot_type: str  # 'external' or 'shared'
    name: Optional[str]
    description: Optional[str]
    status: str
    
    # External bot fields
    api_url: Optional[str] = None
    
    # Shared bot fields
    config_template: Optional[str] = None
    is_public: Optional[bool] = None
    exposed_host_port: Optional[int] = None
    
    # Health information
    last_ping: Optional[datetime] = None
    connection_error: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BotStatusResponse(BaseModel):
    """Bot status response with real-time data"""
    bot_id: str
    bot_type: str
    status: str
    message: str
    connection_health: Optional[Dict[str, Any]] = None
    bot_data: Optional[Dict[str, Any]] = None  # Live data from FreqTrade API
    
    class Config:
        schema_extra = {
            "example": {
                "bot_id": "bot_123",
                "bot_type": "external",
                "status": "running",
                "message": "Bot is running normally",
                "connection_health": {
                    "last_ping": "2024-01-01T12:00:00Z",
                    "response_time": 0.156,
                    "success": True
                },
                "bot_data": {
                    "state": "running",
                    "trades_count": 15,
                    "current_balance": 1250.50
                }
            }
        }


class SharedBotMarketplace(BaseModel):
    """Schema for shared bot marketplace listing"""
    bot_id: str
    name: str
    description: str
    config_template: str
    subscribers_count: int
    performance_30d: Optional[float] = None  # 30-day performance percentage
    risk_level: str  # 'low', 'medium', 'high'
    strategy_type: str  # 'dca', 'grid', 'momentum', etc.
    
    class Config:
        schema_extra = {
            "example": {
                "bot_id": "shared_conservative_btc",
                "name": "Conservative BTC Strategy",
                "description": "Low-risk DCA strategy for BTC/USDT with proven track record",
                "config_template": "conservative_btc_v1",
                "subscribers_count": 156,
                "performance_30d": 8.5,
                "risk_level": "low",
                "strategy_type": "dca"
            }
        }


class BotSubscription(BaseModel):
    """Schema for subscribing to a shared bot"""
    shared_bot_id: str
    allocation_amount: float  # Amount to allocate to this bot
    
    class Config:
        schema_extra = {
            "example": {
                "shared_bot_id": "shared_conservative_btc",
                "allocation_amount": 500.0
            }
        }