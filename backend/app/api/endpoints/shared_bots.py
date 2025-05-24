from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.schemas.bot_schemas import (
    SharedBotMarketplace,
    BotSubscription,
    BotResponse
)
from app.db import session as db_session
from app.crud import crud_bot
from app.models import user as models_user, bot as models_bot
from app.api import deps

router = APIRouter()


@router.get("/marketplace", response_model=List[SharedBotMarketplace])
async def get_shared_bots_marketplace(
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Get list of available shared bots in the marketplace
    """
    # Get all public shared bots
    shared_bots = db.query(models_bot.Bot).filter(
        models_bot.Bot.bot_type == "shared",
        models_bot.Bot.is_public == True
    ).all()
    
    marketplace_bots = []
    for bot in shared_bots:
        # Count subscribers for this bot
        subscribers_count = db.query(models_bot.Bot).filter(
            models_bot.Bot.config_template == bot.config_template,
            models_bot.Bot.tenant_id != bot.tenant_id  # Don't count the original
        ).count()
        
        marketplace_bots.append(SharedBotMarketplace(
            bot_id=bot.bot_id,
            name=bot.name or "Unnamed Strategy",
            description=bot.description or "No description available",
            config_template=bot.config_template or "default",
            subscribers_count=subscribers_count,
            performance_30d=None,  # TODO: Calculate actual performance
            risk_level="medium",   # TODO: Determine from config
            strategy_type="dca"    # TODO: Determine from config
        ))
    
    return marketplace_bots


@router.post("/subscribe", response_model=BotResponse)
async def subscribe_to_shared_bot(
    subscription: BotSubscription,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Subscribe to a shared bot (creates a copy for the user)
    """
    # Find the shared bot template
    shared_bot = db.query(models_bot.Bot).filter(
        models_bot.Bot.bot_id == subscription.shared_bot_id,
        models_bot.Bot.bot_type == "shared",
        models_bot.Bot.is_public == True
    ).first()
    
    if not shared_bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared bot not found or not available"
        )
    
    # Check if user already subscribed to this bot
    existing_subscription = db.query(models_bot.Bot).filter(
        models_bot.Bot.tenant_id == current_user.tenant_id,
        models_bot.Bot.config_template == shared_bot.config_template,
        models_bot.Bot.bot_type == "shared"
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already subscribed to this bot strategy"
        )
    
    # Create user's copy of the shared bot
    import uuid
    user_bot_id = f"shared_{current_user.tenant_id}_{str(uuid.uuid4())[:8]}"
    
    db_bot_data = {
        "bot_id": user_bot_id,
        "tenant_id": current_user.tenant_id,
        "bot_type": "shared",
        "name": f"My {shared_bot.name}",
        "description": shared_bot.description,
        "config_template": shared_bot.config_template,
        "is_public": False,  # User's copy is private
        "status": "subscribed"
    }
    
    user_bot = crud_bot.create_bot(db, bot_data=db_bot_data, tenant_id=current_user.tenant_id)
    
    return BotResponse(
        id=user_bot.id,
        bot_id=user_bot.bot_id,
        tenant_id=user_bot.tenant_id,
        bot_type=user_bot.bot_type,
        name=user_bot.name,
        description=user_bot.description,
        status=user_bot.status,
        config_template=user_bot.config_template,
        is_public=user_bot.is_public,
        created_at=user_bot.created_at,
        updated_at=user_bot.updated_at
    )


@router.delete("/unsubscribe/{bot_id}")
async def unsubscribe_from_shared_bot(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Unsubscribe from a shared bot
    """
    # Find user's shared bot subscription
    user_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    
    if not user_bot or user_bot.bot_type != "shared":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared bot subscription not found"
        )
    
    # Remove the subscription
    crud_bot.remove_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    
    return {
        "success": True,
        "message": f"Successfully unsubscribed from {user_bot.name}"
    }


@router.get("/my-subscriptions", response_model=List[BotResponse])
async def get_my_shared_bot_subscriptions(
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Get user's shared bot subscriptions
    """
    user_shared_bots = db.query(models_bot.Bot).filter(
        models_bot.Bot.tenant_id == current_user.tenant_id,
        models_bot.Bot.bot_type == "shared"
    ).all()
    
    return [
        BotResponse(
            id=bot.id,
            bot_id=bot.bot_id,
            tenant_id=bot.tenant_id,
            bot_type=bot.bot_type,
            name=bot.name,
            description=bot.description,
            status=bot.status,
            config_template=bot.config_template,
            is_public=bot.is_public,
            created_at=bot.created_at,
            updated_at=bot.updated_at
        )
        for bot in user_shared_bots
    ]


@router.get("/{bot_id}/performance")
async def get_shared_bot_performance(
    bot_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Get performance data for a shared bot
    """
    user_bot = crud_bot.get_bot(db, bot_id=bot_id, tenant_id=current_user.tenant_id)
    
    if not user_bot or user_bot.bot_type != "shared":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared bot not found"
        )
    
    # TODO: Get actual performance data from the shared bot instance
    # For now, return mock data
    return {
        "bot_id": bot_id,
        "strategy": user_bot.config_template,
        "performance_data": {
            "total_return": 0.0,
            "monthly_return": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0
        },
        "message": "Performance tracking not yet implemented for shared bots"
    }


# Admin endpoints for managing shared bot templates

@router.post("/templates", response_model=BotResponse)
async def create_shared_bot_template(
    shared_bot_data: dict,  # TODO: Create proper schema
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_user),
):
    """
    Create a new shared bot template (admin only)
    """
    # TODO: Add admin permission check
    
    import uuid
    template_bot_id = f"template_{str(uuid.uuid4())[:8]}"
    
    db_bot_data = {
        "bot_id": template_bot_id,
        "tenant_id": "platform",  # Special tenant for platform bots
        "bot_type": "shared",
        "name": shared_bot_data.get("name"),
        "description": shared_bot_data.get("description"),
        "config_template": shared_bot_data.get("config_template"),
        "is_public": True,
        "status": "template"
    }
    
    template_bot = crud_bot.create_bot(db, bot_data=db_bot_data, tenant_id="platform")
    
    return BotResponse(
        id=template_bot.id,
        bot_id=template_bot.bot_id,
        tenant_id=template_bot.tenant_id,
        bot_type=template_bot.bot_type,
        name=template_bot.name,
        description=template_bot.description,
        status=template_bot.status,
        config_template=template_bot.config_template,
        is_public=template_bot.is_public,
        created_at=template_bot.created_at,
        updated_at=template_bot.updated_at
    )