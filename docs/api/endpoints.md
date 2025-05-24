# TradeWise API Documentation

## 🌐 Base URL
```
http://localhost:8000/api/v1
```

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## 📝 API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "tenant_id": "uuid-tenant-id"
}
```

#### Login
```http
POST /auth/token
```

**Request Body (Form Data):**
```
username=user@example.com
password=secure_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### External Bots

#### Test Bot Connection
```http
POST /external-bots/test-connection
```

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "api_url": "http://192.168.1.100:8080",
  "api_token": "bot-api-token"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Successfully connected to trading bot",
  "bot_info": {
    "state": "running",
    "trades_count": 15,
    "current_balance": 1250.50
  },
  "connection_status": "healthy"
}
```

**Response (Failure):**
```json
{
  "success": false,
  "message": "Bot did not respond within timeout period",
  "error": "Connection timeout",
  "connection_status": "failed"
}
```

#### Connect External Bot
```http
POST /external-bots/connect
```

**Request Body:**
```json
{
  "name": "My Trading Bot",
  "description": "BTC/ETH trading bot on my home server",
  "api_url": "http://192.168.1.100:8080",
  "api_token": "bot-api-token"
}
```

**Response:**
```json
{
  "id": 1,
  "bot_id": "ext_tenant_abc123",
  "tenant_id": "uuid-tenant-id",
  "bot_type": "external",
  "name": "My Trading Bot",
  "description": "BTC/ETH trading bot on my home server",
  "status": "connected",
  "api_url": "http://192.168.1.100:8080",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### Get Bot Status
```http
GET /external-bots/{bot_id}/status
```

**Response:**
```json
{
  "bot_id": "ext_tenant_abc123",
  "bot_type": "external",
  "status": "running",
  "message": "Bot is running normally",
  "connection_health": {
    "last_ping": "2024-01-01T12:00:00Z",
    "success": true
  },
  "bot_data": {
    "state": "running",
    "trades_count": 15,
    "current_balance": 1250.50
  }
}
```

#### Start Bot
```http
POST /external-bots/{bot_id}/start
```

**Response:**
```json
{
  "success": true,
  "message": "Start command sent to bot"
}
```

#### Stop Bot
```http
POST /external-bots/{bot_id}/stop
```

**Response:**
```json
{
  "success": true,
  "message": "Stop command sent to bot"
}
```

#### Get Bot Performance
```http
GET /external-bots/{bot_id}/performance
```

**Response:**
```json
{
  "bot_id": "ext_tenant_abc123",
  "performance_data": {
    "total_profit": 125.50,
    "profit_percentage": 8.5,
    "total_trades": 47,
    "winning_trades": 31,
    "losing_trades": 16
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Get Bot Trades
```http
GET /external-bots/{bot_id}/trades?limit=50
```

**Response:**
```json
{
  "bot_id": "ext_tenant_abc123",
  "trades": [
    {
      "trade_id": 123,
      "pair": "BTC/USDT",
      "side": "buy",
      "amount": 0.001,
      "price": 45000.0,
      "profit": 12.50,
      "timestamp": "2024-01-01T11:30:00Z"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Disconnect Bot
```http
DELETE /external-bots/{bot_id}
```

**Response:**
```json
{
  "success": true,
  "message": "External bot ext_tenant_abc123 disconnected successfully"
}
```

### Shared Bots (Platform Bots)

#### Get My Bots
```http
GET /bots/
```

**Response:**
```json
[
  {
    "id": 1,
    "bot_id": "ext_tenant_abc123",
    "bot_type": "external",
    "name": "My Trading Bot",
    "status": "running",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

#### Get Shared Bots Marketplace
```http
GET /shared-bots/marketplace
```

**Response:**
```json
[
  {
    "bot_id": "shared_conservative_btc",
    "name": "Conservative BTC Strategy",
    "description": "Low-risk DCA strategy for BTC/USDT with proven track record",
    "config_template": "conservative_btc_v1",
    "subscribers_count": 156,
    "performance_30d": 8.5,
    "risk_level": "low",
    "strategy_type": "dca"
  }
]
```

#### Subscribe to Shared Bot
```http
POST /shared-bots/subscribe
```

**Request Body:**
```json
{
  "shared_bot_id": "shared_conservative_btc",
  "allocation_amount": 500.0
}
```

**Response:**
```json
{
  "id": 2,
  "bot_id": "sub_tenant_xyz789",
  "bot_type": "shared",
  "name": "Conservative BTC Strategy",
  "status": "starting",
  "allocation_amount": 500.0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### Get My Subscriptions
```http
GET /shared-bots/my-subscriptions
```

**Response:**
```json
[
  {
    "id": 2,
    "bot_id": "sub_tenant_xyz789",
    "bot_type": "shared",
    "name": "Conservative BTC Strategy",
    "status": "running",
    "allocation_amount": 500.0,
    "performance_7d": 2.1,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### WebSocket Endpoints

#### Bot Status Updates
```
ws://localhost:8000/api/v1/ws/bot-status/{bot_id}
```

**Authentication:** Include JWT token as query parameter:
```
ws://localhost:8000/api/v1/ws/bot-status/bot123?token=<jwt_token>
```

**Message Format:**
```json
{
  "type": "status_update",
  "bot_id": "bot123",
  "status": "running",
  "data": {
    "current_balance": 1275.30,
    "trades_today": 3,
    "last_trade": "2024-01-01T11:45:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 404  | Not Found |
| 409  | Conflict |
| 422  | Validation Error |
| 500  | Internal Server Error |
| 503  | Service Unavailable |

## 🚨 Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "uuid-request-id"
}
```

## 🔄 Rate Limiting (Future)

| Endpoint Pattern | Limit |
|------------------|-------|
| `/auth/*` | 5 requests/minute |
| `/external-bots/test-connection` | 10 requests/minute |
| `/*` (General) | 100 requests/minute |

## 📝 Request/Response Examples

### Complete Bot Connection Flow

1. **Test Connection**
```bash
curl -X POST http://localhost:8000/api/v1/external-bots/test-connection \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "api_url": "http://192.168.1.100:8080",
    "api_token": "bot-token"
  }'
```

2. **Connect Bot (if test successful)**
```bash
curl -X POST http://localhost:8000/api/v1/external-bots/connect \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Bot",
    "description": "Trading bot description",
    "api_url": "http://192.168.1.100:8080",
    "api_token": "bot-token"
  }'
```

3. **Monitor Status**
```bash
curl -X GET http://localhost:8000/api/v1/external-bots/ext_tenant_abc123/status \
  -H "Authorization: Bearer <token>"
```

## 🔧 SDK Examples (Future)

### Python SDK
```python
from tradewise_sdk import TradeWiseClient

client = TradeWiseClient(api_key="your-api-key")

# Test bot connection
result = client.test_bot_connection(
    api_url="http://192.168.1.100:8080",
    api_token="bot-token"
)

# Connect bot if test passes
if result.success:
    bot = client.connect_external_bot(
        name="My Bot",
        api_url="http://192.168.1.100:8080",
        api_token="bot-token"
    )
```

### JavaScript SDK
```javascript
import { TradeWiseClient } from '@tradewise/sdk';

const client = new TradeWiseClient({ apiKey: 'your-api-key' });

// Test and connect bot
const testResult = await client.testBotConnection({
  apiUrl: 'http://192.168.1.100:8080',
  apiToken: 'bot-token'
});

if (testResult.success) {
  const bot = await client.connectExternalBot({
    name: 'My Bot',
    apiUrl: 'http://192.168.1.100:8080',
    apiToken: 'bot-token'
  });
}
```