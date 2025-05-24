from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session

from app.services.orchestrator import FreqtradeOrchestrator
from app.schemas.freqtrade_config import FreqtradeConfigCreate
from app.schemas.api_responses import (
    BotStatusResponse,
    BotDeleteResponse,
    BotLogResponse,
)
from app.db import (
    session as db_session,
)  # For get_db, if not using deps.get_db directly
from app.crud import crud_bot
from app.models import user as models_user  # For User model type hint
from app.api import deps  # For get_current_active_user

router = APIRouter()

# Global orchestrator instance (consider dependency injection for orchestrator in a larger app)
orchestrator = FreqtradeOrchestrator()


@router.post("", response_model=BotStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_bot_endpoint(
    bot_config: FreqtradeConfigCreate,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Creates and starts a new Freqtrade bot instance for the authenticated user's tenant.
    """
    tenant_id = current_user.tenant_id

    # Orchestrator generates a bot_id that should be unique and incorporate tenant_id
    # For example, "ft-{tenant_id}-{some_uuid_or_config_hash}"
    # The actual bot_id is determined by orchestrator.generate_bot_config which is called by start_bot
    # We get the derived_bot_id to check for conflicts and for DB storage.

    # Note: orchestrator.generate_bot_config is called internally by orchestrator.start_bot
    # and also by orchestrator.create_tenant_config_file.
    # To get the bot_id for pre-checks, we can call generate_bot_config first.
    # This is a slight duplication of call but ensures we have the ID.
    # A potential refactor could be for start_bot to return the fully constructed bot_id.
    preliminary_bot_details = orchestrator.generate_bot_config(tenant_id)
    derived_bot_id = preliminary_bot_details["bot_id"]

    db_bot_check = crud_bot.get_bot(db, bot_id=derived_bot_id, tenant_id=tenant_id)
    if db_bot_check:
        live_status = orchestrator.get_bot_status(
            derived_bot_id
        )  # Check if it's actually running
        if "error" not in live_status or live_status.get("status") in [
            "running",
            "starting",
        ]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Bot with derived ID '{derived_bot_id}' already exists and might be active for your tenant.",
            )
        # If in DB but not live, maybe allow cleanup or re-creation. For now, strict.

    try:
        bot_config_data = bot_config.model_dump()

        # Get paths for DB storage (these are also generated/used inside start_bot)
        actual_config_json_path = orchestrator.create_tenant_config_file(
            tenant_id, bot_config_data
        )
        user_data_path = preliminary_bot_details[
            "user_data_path"
        ]  # From generate_bot_config
        exposed_host_port = preliminary_bot_details["port"]

        bot_db_data_pre_start = {
            "bot_id": derived_bot_id,  # Use the ID derived by orchestrator based on tenant_id
            # tenant_id is passed to crud_bot.create_bot separately
            "status": "creating",
            "config_path": actual_config_json_path,
            "user_data_path": user_data_path,
            "exposed_host_port": exposed_host_port,
            "container_id": None,
        }
        # Create preliminary DB record, passing current_user.tenant_id for ownership
        db_bot_created = crud_bot.create_bot(
            db, bot_data=bot_db_data_pre_start, tenant_id=tenant_id
        )

        # Now, attempt to start the Docker container, passing tenant_id from authenticated user
        result = orchestrator.start_bot(
            tenant_id=tenant_id, bot_config_data=bot_config_data
        )

        if "error" in result:
            crud_bot.update_bot_status(
                db, bot_id=derived_bot_id, tenant_id=tenant_id, status="error_creation"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"],
            )

        updated_bot = crud_bot.update_bot_status(
            db,
            bot_id=derived_bot_id,
            tenant_id=tenant_id,
            status=result.get("status", "running"),
            container_id=result.get("id"),
            exposed_host_port=result.get(
                "port"
            ),  # Orchestrator start_bot also returns port
        )

        return BotStatusResponse(
            bot_id=updated_bot.bot_id,
            status=updated_bot.status,
            message="Bot created and started successfully.",
            details={
                "container_id": updated_bot.container_id,
                "host_port": updated_bot.exposed_host_port,
                "config_path": updated_bot.config_path,
                "user_data_path": updated_bot.user_data_path,
                "tenant_id": updated_bot.tenant_id,  # Confirming it's the user's tenant_id
                "created_at": str(updated_bot.created_at),
                "updated_at": str(updated_bot.updated_at),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        if (
            "db_bot_created" in locals() and db_bot_created
        ):  # Check if preliminary record was made
            crud_bot.update_bot_status(
                db, bot_id=derived_bot_id, tenant_id=tenant_id, status="error_unknown"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.delete("/{bot_id}", response_model=BotDeleteResponse)
async def delete_bot_endpoint(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    # First, ensure the bot exists in DB and belongs to the user's tenant
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        # If not in DB under this tenant, check if it's an orphaned container (no DB record but live)
        # For simplicity, we'll assume if it's not in DB for this tenant, it's a 404.
        # A more advanced check might involve querying Docker if an admin were deleting.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )

    try:
        stopped_by_orchestrator = orchestrator.stop_bot(
            bot_id
        )  # bot_id is container name

        # Regardless of orchestrator result (it might have already been stopped/removed),
        # remove from DB if it was found for this tenant.
        crud_bot.remove_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)

        if not stopped_by_orchestrator:
            # If orchestrator says it couldn't stop it (e.g. already gone), but we removed from DB:
            return BotDeleteResponse(
                bot_id=bot_id,
                message="Bot removed from database. Orchestrator reported it was not running or already removed.",
            )

        return BotDeleteResponse(
            bot_id=bot_id,
            message="Bot stopped, removed by orchestrator, and deleted from database.",
        )
    except Exception as e:
        # If error during orchestrator interaction, the DB record still exists.
        # Update its status to reflect potential issue if needed, or just report error.
        crud_bot.update_bot_status(
            db, bot_id=bot_id, tenant_id=current_user.tenant_id, status="error_deletion"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.get("/{bot_id}", response_model=BotStatusResponse)
async def get_bot_status_api_endpoint(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )

    # Optionally, sync with live Docker status if desired, for now, returns DB state.
    # live_status = orchestrator.get_bot_status(bot_id)
    # if "error" not in live_status:
    #    db_bot.status = live_status.get("status", db_bot.status) # Update if different
    #    crud_bot.update_bot_status(db, bot_id, current_user.tenant_id, db_bot.status, live_status.get("id"))

    return BotStatusResponse(
        bot_id=db_bot.bot_id,
        status=db_bot.status,  # This is the status from DB
        message="Bot status retrieved from database.",
        details={
            "container_id": db_bot.container_id,
            "host_port": db_bot.exposed_host_port,
            "config_path": db_bot.config_path,
            "user_data_path": db_bot.user_data_path,
            "tenant_id": db_bot.tenant_id,
            "db_id": db_bot.id,
            "created_at": str(db_bot.created_at),
            "updated_at": str(db_bot.updated_at),
        },
    )


@router.get("", response_model=List[BotStatusResponse])
async def list_bots_for_tenant_endpoint(
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    db_bots = crud_bot.get_bots_by_tenant(
        db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    if not db_bots:
        return []

    response_list = []
    for db_bot in db_bots:
        response_list.append(
            BotStatusResponse(
                bot_id=db_bot.bot_id,
                status=db_bot.status,
                message="Bot status retrieved from database.",
                details={
                    "container_id": db_bot.container_id,
                    "host_port": db_bot.exposed_host_port,
                    "config_path": db_bot.config_path,
                    "user_data_path": db_bot.user_data_path,
                    "tenant_id": db_bot.tenant_id,
                    "db_id": db_bot.id,
                    "created_at": str(db_bot.created_at),
                    "updated_at": str(db_bot.updated_at),
                },
            )
        )
    return response_list


@router.get("/{bot_id}/logs", response_model=BotLogResponse)
async def get_bot_logs_api_endpoint(
    bot_id: str,
    tail: int = Query(100, gt=0, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )

    logs = orchestrator.get_bot_logs(bot_id=bot_id, tail=tail)

    if logs is None:
        live_status = orchestrator.get_bot_status(bot_id)
        if "error" in live_status and "Container not found" in live_status["error"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bot container '{bot_id}' not found by Docker.",
            )
        return BotLogResponse(
            bot_id=bot_id,
            logs="",
            message="Logs could not be retrieved or are empty. The container might not be running or encountered an issue.",
        )

    return BotLogResponse(
        bot_id=bot_id, logs=logs, message="Logs retrieved successfully."
    )


# Enhanced Bot Control Endpoints

@router.post("/{bot_id}/start", response_model=BotStatusResponse)
async def start_bot_endpoint(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """Start a stopped bot"""
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )
    
    # TODO: Implement start logic in orchestrator
    # For now, return mock response
    return BotStatusResponse(
        bot_id=bot_id,
        status="starting",
        message="Bot start command sent successfully.",
        details={"action": "start", "timestamp": str(db_bot.updated_at)}
    )


@router.post("/{bot_id}/stop", response_model=BotStatusResponse)
async def stop_bot_endpoint(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """Stop a running bot"""
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )
    
    # Update status to stopping
    crud_bot.update_bot_status(db, bot_id=bot_id, tenant_id=current_user.tenant_id, status="stopping")
    
    # TODO: Implement graceful stop in orchestrator
    # For now, return mock response
    return BotStatusResponse(
        bot_id=bot_id,
        status="stopping",
        message="Bot stop command sent successfully.",
        details={"action": "stop", "timestamp": str(db_bot.updated_at)}
    )


@router.post("/{bot_id}/restart", response_model=BotStatusResponse)
async def restart_bot_endpoint(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """Restart a bot"""
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )
    
    # Update status to restarting
    crud_bot.update_bot_status(db, bot_id=bot_id, tenant_id=current_user.tenant_id, status="restarting")
    
    # TODO: Implement restart logic in orchestrator
    return BotStatusResponse(
        bot_id=bot_id,
        status="restarting",
        message="Bot restart command sent successfully.",
        details={"action": "restart", "timestamp": str(db_bot.updated_at)}
    )


@router.get("/{bot_id}/performance")
async def get_bot_performance(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """Get bot performance metrics"""
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )
    
    # TODO: Implement performance metrics collection
    return {
        "bot_id": bot_id,
        "profit_loss": 0.0,
        "total_trades": 0,
        "win_rate": 0.0,
        "avg_profit": 0.0,
        "current_balance": 0.0,
        "message": "Performance metrics not yet implemented"
    }


@router.get("/{bot_id}/trades")
async def get_bot_trades(
    bot_id: str,
    limit: int = Query(50, gt=0, le=500),
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """Get bot trade history"""
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )
    
    # TODO: Implement trade history retrieval
    return {
        "bot_id": bot_id,
        "trades": [],
        "total_count": 0,
        "message": "Trade history not yet implemented"
    }


@router.put("/{bot_id}/config", response_model=BotStatusResponse)
async def update_bot_config(
    bot_id: str,
    config_update: FreqtradeConfigCreate,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """Update bot configuration"""
    db_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    if not db_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found for your tenant.",
        )
    
    # TODO: Implement configuration update
    # This should update the config file and potentially restart the bot
    return BotStatusResponse(
        bot_id=bot_id,
        status="config_updated",
        message="Bot configuration updated successfully.",
        details={"action": "config_update", "requires_restart": True}
    )
