from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.session import Base


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # bot_id is the unique identifier for the bot instance
    bot_id = Column(String, unique=True, index=True, nullable=False)
    tenant_id = Column(String, index=True, nullable=False)
    
    # Bot type: 'external' for user's own bots, 'shared' for platform-managed bots
    bot_type = Column(String, nullable=False, default="external")  # 'external' or 'shared'
    
    # Status of the bot connection/instance
    status = Column(
        String, nullable=False, default="unknown"
    )  # e.g., "connected", "running", "stopped", "error", "disconnected"

    # Bot metadata
    name = Column(String, nullable=True)  # Human-readable name
    description = Column(Text, nullable=True)  # Bot description
    
    # External bot connection details (for user's own bots)
    api_url = Column(String, nullable=True)  # FreqTrade bot API URL (e.g., http://user-server:8080)
    
    # Authentication method: 'token' or 'basic'
    auth_method = Column(String, nullable=True, default="token")  # 'token' or 'basic'
    
    # Token-based authentication
    api_token = Column(String, nullable=True)  # FreqTrade bot API token for authentication
    
    # Username/password authentication  
    username = Column(String, nullable=True)  # Username for basic auth
    password = Column(String, nullable=True)  # Password for basic auth (encrypted)
    
    # Shared bot details (for platform-managed bots)
    config_template = Column(String, nullable=True)  # Configuration template for shared bots
    is_public = Column(Boolean, default=False)  # Whether shared bot is available to all users
    
    # Legacy fields (for backward compatibility and shared bots)
    config_path = Column(String, nullable=True)  # Path to config.json (shared bots only)
    user_data_path = Column(String, nullable=True)  # Path to user_data (shared bots only)
    exposed_host_port = Column(Integer, nullable=True)  # Port (shared bots only)
    container_id = Column(String, nullable=True)  # Docker container ID (shared bots only)

    # Connection health
    last_ping = Column(DateTime(timezone=True), nullable=True)  # Last successful API ping
    connection_error = Column(Text, nullable=True)  # Last connection error message

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Bot(id={self.id}, bot_id='{self.bot_id}', tenant_id='{self.tenant_id}', status='{self.status}')>"
