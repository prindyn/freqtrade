from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import uuid

from app.schemas.bot_schemas import (
    ExternalBotCreate,
    BotConnectionTest,
    BotResponse,
    BotStatusResponse,
)
from app.services.external_bot_manager import ExternalBotManager
from app.db import session as db_session
from app.crud import crud_bot
from app.models import user as models_user, bot as models_bot
from app.api import deps
from app.core.logging import get_logger, log_business_event, log_security_event

logger = get_logger("external_bots_api")

router = APIRouter()
external_bot_manager = ExternalBotManager()


@router.get("", response_model=List[BotResponse])
async def list_external_bots(
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Get all external bots for the current user/tenant
    """
    logger.info(
        "User requesting external bots list",
        extra={
            "event_type": "external_bots_list_request",
            "user_id": str(current_user.id),
            "tenant_id": current_user.tenant_id,
        }
    )
    
    # Get all external bots for this tenant
    db_bots = (
        db.query(models_bot.Bot)
        .filter(
            models_bot.Bot.tenant_id == current_user.tenant_id,
            models_bot.Bot.bot_type == "external",
        )
        .all()
    )
    
    bots_response = []
    for db_bot in db_bots:
        bots_response.append(BotResponse(
            id=db_bot.id,
            bot_id=db_bot.bot_id,
            tenant_id=db_bot.tenant_id,
            bot_type=db_bot.bot_type,
            name=db_bot.name,
            description=db_bot.description,
            status=db_bot.status,
            api_url=db_bot.api_url,
            created_at=db_bot.created_at,
            updated_at=db_bot.updated_at,
        ))
    
    logger.info(
        f"Returning {len(bots_response)} external bots for user",
        extra={
            "event_type": "external_bots_list_response",
            "user_id": str(current_user.id),
            "tenant_id": current_user.tenant_id,
            "bot_count": len(bots_response),
        }
    )
    
    return bots_response


@router.post("/test-connection")
async def test_bot_connection(
    connection_test: BotConnectionTest,
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Test connection to an external trading bot before adding it
    """
    logger.info(
        "User testing bot connection",
        extra={
            "event_type": "bot_connection_test_request",
            "user_id": str(current_user.id),
            "tenant_id": current_user.tenant_id,
            "api_url": connection_test.api_url
        }
    )
    
    result = external_bot_manager.test_bot_connection(
        api_url=connection_test.api_url,
        auth_method=connection_test.auth_method,
        api_token=connection_test.api_token,
        username=connection_test.username,
        password=connection_test.password
    )

    if result["success"]:
        log_business_event(
            event_type="bot_connection_test_success",
            description="User successfully tested bot connection",
            user_id=str(current_user.id),
            tenant_id=current_user.tenant_id,
            api_url=connection_test.api_url
        )
        
        return {
            "success": True,
            "message": "Successfully connected to trading bot",
            "bot_info": result.get("bot_info", {}),
            "connection_status": "healthy",
        }
    else:
        logger.warning(
            "Bot connection test failed",
            extra={
                "event_type": "bot_connection_test_failure",
                "user_id": str(current_user.id),
                "tenant_id": current_user.tenant_id,
                "api_url": connection_test.api_url,
                "error": result.get("error")
            }
        )
        
        return {
            "success": False,
            "message": result["message"],
            "error": result.get("error", "Unknown error"),
            "connection_status": "failed",
        }


@router.post(
    "/connect", response_model=BotResponse, status_code=status.HTTP_201_CREATED
)
async def connect_external_bot(
    bot_data: ExternalBotCreate,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Connect to an external FreqTrade bot and add it to user's dashboard
    """
    # First test the connection
    connection_result = external_bot_manager.test_bot_connection(
        api_url=bot_data.api_url,
        auth_method=bot_data.auth_method,
        api_token=bot_data.api_token,
        username=bot_data.username,
        password=bot_data.password
    )

    if not connection_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to bot: {connection_result['message']}",
        )

    # Generate unique bot_id
    bot_id = f"ext_{current_user.tenant_id}_{str(uuid.uuid4())[:8]}"

    # Check if bot with same URL already exists for this tenant
    existing_bot = (
        db.query(models_bot.Bot)
        .filter(
            models_bot.Bot.tenant_id == current_user.tenant_id,
            models_bot.Bot.api_url == bot_data.api_url,
            models_bot.Bot.bot_type == "external",
        )
        .first()
    )

    if existing_bot:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A bot with this API URL is already connected",
        )

    # Create bot record
    db_bot_data = {
        "bot_id": bot_id,
        "tenant_id": current_user.tenant_id,
        "bot_type": "external",
        "name": bot_data.name,
        "description": bot_data.description,
        "api_url": bot_data.api_url,
        "auth_method": bot_data.auth_method,
        "api_token": bot_data.api_token,
        "username": bot_data.username,
        "password": bot_data.password,  # Note: This should be encrypted in production
        "status": "connected",
    }

    db_bot = crud_bot.create_bot(
        db, bot_data=db_bot_data, tenant_id=current_user.tenant_id
    )

    return BotResponse(
        id=db_bot.id,
        bot_id=db_bot.bot_id,
        tenant_id=db_bot.tenant_id,
        bot_type=db_bot.bot_type,
        name=db_bot.name,
        description=db_bot.description,
        status=db_bot.status,
        api_url=db_bot.api_url,
        created_at=db_bot.created_at,
        updated_at=db_bot.updated_at,
    )


@router.get("/{bot_id}/status", response_model=BotStatusResponse)
async def get_external_bot_status(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Get real-time status from an external FreqTrade bot
    """
    # Get bot from database
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot or db_bot.bot_type != "external":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="External bot not found"
        )

    # Get live status from the bot
    status_result = external_bot_manager.get_bot_status(
        api_url=db_bot.api_url,
        auth_method=db_bot.auth_method or "token",
        api_token=db_bot.api_token,
        username=db_bot.username,
        password=db_bot.password
    )

    if status_result["success"]:
        # Update last ping time
        crud_bot.update_bot_status(
            db,
            bot_id=bot_id,
            tenant_id=current_user.tenant_id,
            status="running",
            connection_error=None,
        )

        # Ensure bot_data is always a dictionary
        bot_data = status_result["data"]
        if isinstance(bot_data, list):
            # If the API returns a list (e.g., trades), wrap it in a dictionary
            bot_data = {"trades": bot_data}
        elif not isinstance(bot_data, dict):
            # If it's neither list nor dict, wrap it in a generic structure
            bot_data = {"raw_data": bot_data}

        return BotStatusResponse(
            bot_id=bot_id,
            bot_type="external",
            status="running",
            message="Bot is running normally",
            connection_health={
                "last_ping": status_result["timestamp"],
                "success": True,
            },
            bot_data=bot_data,
        )
    else:
        # Update connection error
        crud_bot.update_bot_status(
            db,
            bot_id=bot_id,
            tenant_id=current_user.tenant_id,
            status="error",
            connection_error=status_result["error"],
        )

        return BotStatusResponse(
            bot_id=bot_id,
            bot_type="external",
            status="error",
            message=f"Connection failed: {status_result['message']}",
            connection_health={"success": False, "error": status_result["error"]},
        )


@router.post("/{bot_id}/start")
async def start_external_bot(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Send start command to external FreqTrade bot
    """
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot or db_bot.bot_type != "external":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="External bot not found"
        )

    result = external_bot_manager.start_bot(
        api_url=db_bot.api_url,
        auth_method=db_bot.auth_method or "token",
        api_token=db_bot.api_token,
        username=db_bot.username,
        password=db_bot.password
    )

    if result["success"]:
        crud_bot.update_bot_status(
            db, bot_id=bot_id, tenant_id=current_user.tenant_id, status="starting"
        )
        return {"success": True, "message": "Start command sent to bot"}
    else:
        return {
            "success": False,
            "message": result["message"],
            "error": result["error"],
        }


@router.post("/{bot_id}/stop")
async def stop_external_bot(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Send stop command to external FreqTrade bot
    """
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot or db_bot.bot_type != "external":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="External bot not found"
        )

    result = external_bot_manager.stop_bot(
        api_url=db_bot.api_url,
        auth_method=db_bot.auth_method or "token",
        api_token=db_bot.api_token,
        username=db_bot.username,
        password=db_bot.password
    )

    if result["success"]:
        crud_bot.update_bot_status(
            db, bot_id=bot_id, tenant_id=current_user.tenant_id, status="stopping"
        )
        return {"success": True, "message": "Stop command sent to bot"}
    else:
        return {
            "success": False,
            "message": result["message"],
            "error": result["error"],
        }


@router.get("/{bot_id}/performance")
async def get_external_bot_performance(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Get performance metrics from external FreqTrade bot
    """
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot or db_bot.bot_type != "external":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="External bot not found"
        )

    result = external_bot_manager.get_bot_performance(
        api_url=db_bot.api_url,
        auth_method=db_bot.auth_method or "token",
        api_token=db_bot.api_token,
        username=db_bot.username,
        password=db_bot.password
    )

    if result["success"]:
        return {
            "bot_id": bot_id,
            "performance_data": result["data"],
            "timestamp": result["timestamp"],
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to get performance data: {result['message']}",
        )


@router.get("/{bot_id}/trades")
async def get_external_bot_trades(
    bot_id: str,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Get trade history from external FreqTrade bot
    """
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot or db_bot.bot_type != "external":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="External bot not found"
        )

    result = external_bot_manager.get_bot_trades(
        api_url=db_bot.api_url,
        auth_method=db_bot.auth_method or "token",
        api_token=db_bot.api_token,
        username=db_bot.username,
        password=db_bot.password,
        limit=limit
    )

    if result["success"]:
        return {
            "bot_id": bot_id,
            "trades": result["data"],
            "timestamp": result["timestamp"],
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to get trades: {result['message']}",
        )


@router.delete("/{bot_id}")
async def disconnect_external_bot(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Disconnect an external bot (remove from dashboard)
    """
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot or db_bot.bot_type != "external":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="External bot not found"
        )

    # Remove bot from database
    crud_bot.remove_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)

    return {
        "success": True,
        "message": f"External bot {bot_id} disconnected successfully",
    }
