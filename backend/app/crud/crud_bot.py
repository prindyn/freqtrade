from sqlalchemy.orm import Session
from app.models import bot as models_bot  # Alias to avoid confusion
from app.schemas import freqtrade_config as schemas_ft  # For type hinting if needed
from typing import Optional


def get_bot(db: Session, bot_id: str, tenant_id: str) -> Optional[models_bot.Bot]:
    return (
        db.query(models_bot.Bot)
        .filter(models_bot.Bot.bot_id == bot_id, models_bot.Bot.tenant_id == tenant_id)
        .first()
    )


def get_bots_by_tenant(
    db: Session, tenant_id: str, skip: int = 0, limit: int = 100
) -> list[models_bot.Bot]:
    return (
        db.query(models_bot.Bot)
        .filter(models_bot.Bot.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_bot(db: Session, bot_data: dict, tenant_id: str) -> models_bot.Bot:
    """
    Creates a new Bot record in the database.
    bot_data should contain all necessary fields for the Bot model,
    EXCEPT tenant_id which is provided separately from the authenticated user.
    """
    # Ensure tenant_id from authenticated user is used
    db_bot_data = bot_data.copy()
    db_bot_data["tenant_id"] = tenant_id

    # Ensure bot_id aligns with the tenant_id (e.g. "ft-{tenant_id}-...")
    # The bot_data['bot_id'] should already be correctly formatted by the orchestrator
    # based on the tenant_id passed to it.
    # We can add a check here if necessary:
    # if not db_bot_data['bot_id'].startswith(f"ft-{tenant_id}"):
    #     raise ValueError("bot_id does not match tenant_id prefix")

    db_bot = models_bot.Bot(**db_bot_data)
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot


def update_bot_status(
    db: Session,
    bot_id: str,
    tenant_id: str,
    status: str,
    container_id: Optional[str] = None,
    exposed_host_port: Optional[int] = None,
    connection_error: Optional[str] = None,
) -> Optional[models_bot.Bot]:
    db_bot = get_bot(db, bot_id=bot_id, tenant_id=tenant_id)  # Verify ownership
    if db_bot:
        db_bot.status = status
        if container_id is not None:
            db_bot.container_id = container_id
        if exposed_host_port is not None:
            db_bot.exposed_host_port = exposed_host_port
        if connection_error is not None:
            db_bot.connection_error = connection_error
        db.commit()
        db.refresh(db_bot)
    return db_bot


def update_bot_paths(
    db: Session,
    bot_id: str,
    tenant_id: str,
    config_path: Optional[str] = None,
    user_data_path: Optional[str] = None,
) -> Optional[models_bot.Bot]:
    db_bot = get_bot(db, bot_id=bot_id, tenant_id=tenant_id)  # Verify ownership
    if db_bot:
        if config_path:
            db_bot.config_path = config_path
        if user_data_path:
            db_bot.user_data_path = user_data_path
        db.commit()
        db.refresh(db_bot)
    return db_bot


def remove_bot(db: Session, bot_id: str, tenant_id: str) -> Optional[models_bot.Bot]:
    db_bot = get_bot(db, bot_id=bot_id, tenant_id=tenant_id)  # Verify ownership
    if db_bot:
        db.delete(db_bot)
        db.commit()
    return db_bot
