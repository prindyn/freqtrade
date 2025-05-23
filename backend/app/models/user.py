from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
import uuid  # For tenant_id generation


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # tenant_id will be generated when a user is created.
    # This links the user to their tenant space.
    tenant_id = Column(
        String, index=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return (
            f"<User(id={self.id}, email='{self.email}', tenant_id='{self.tenant_id}')>"
        )
