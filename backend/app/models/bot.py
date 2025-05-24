from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # bot_id is the unique name for the bot instance, often derived from tenant_id, e.g., "ft-tenant-xyz"
    # This will also be the container name.
    bot_id = Column(String, unique=True, index=True, nullable=False)
    tenant_id = Column(String, index=True, nullable=False)
    status = Column(
        String, nullable=False, default="unknown"
    )  # e.g., "creating", "running", "stopped", "error"

    # Paths are stored to know where the bot's configuration and data reside on the host
    config_path = Column(
        String, nullable=True
    )  # Path to the specific config.json used by this bot
    user_data_path = Column(
        String, nullable=True
    )  # Path to the user_data directory for this bot

    exposed_host_port = Column(
        Integer, nullable=True
    )  # The port on the host machine mapped to the bot's API
    container_id = Column(String, nullable=True)  # Docker's internal container ID

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Bot(id={self.id}, bot_id='{self.bot_id}', tenant_id='{self.tenant_id}', status='{self.status}')>"
