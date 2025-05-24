from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas import user as schemas_user
from app.schemas import token as schemas_token
from app.crud import crud_user
from app.core import security
from app.api import deps  # For get_db
from app.core.logging import get_logger, log_business_event, log_security_event

logger = get_logger("auth_api")

router = APIRouter()


@router.post(
    "/register", response_model=schemas_user.User, status_code=status.HTTP_201_CREATED
)
def register_user(user_in: schemas_user.UserCreate, request: Request, db: Session = Depends(deps.get_db)):
    """
    Create new user.
    """
    client_ip = request.client.host if request.client else None
    
    logger.info(
        "User registration attempt",
        extra={
            "event_type": "user_registration_attempt",
            "email": user_in.email,
            "client_ip": client_ip
        }
    )
    
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        log_security_event(
            event_type="registration_duplicate_email",
            description="Registration attempt with existing email",
            ip_address=client_ip,
            email=user_in.email
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    created_user = crud_user.create_user(db=db, user=user_in)
    
    log_business_event(
        event_type="user_registered",
        description="New user registered successfully",
        user_id=str(created_user.id),
        tenant_id=created_user.tenant_id,
        email=created_user.email,
        client_ip=client_ip
    )
    
    return created_user


@router.post("/token", response_model=schemas_token.Token)
def login_for_access_token(
    request: Request,
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username is the email.
    """
    client_ip = request.client.host if request.client else None
    
    logger.info(
        "User login attempt",
        extra={
            "event_type": "user_login_attempt",
            "email": form_data.username,
            "client_ip": client_ip
        }
    )
    
    user = crud_user.get_user_by_email(
        db, email=form_data.username
    )  # form_data.username is the email
    
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        log_security_event(
            event_type="login_failed",
            description="Login attempt with incorrect credentials",
            ip_address=client_ip,
            email=form_data.username
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        log_security_event(
            event_type="login_inactive_user",
            description="Login attempt by inactive user",
            user_id=str(user.id),
            ip_address=client_ip,
            email=user.email
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = security.create_access_token(
        data={"sub": user.email}  # 'sub' (subject) is the user's email
    )
    
    log_business_event(
        event_type="user_logged_in",
        description="User successfully logged in",
        user_id=str(user.id),
        tenant_id=user.tenant_id,
        client_ip=client_ip
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
