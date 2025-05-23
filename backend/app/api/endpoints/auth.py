from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas import user as schemas_user
from app.schemas import token as schemas_token
from app.crud import crud_user
from app.core import security
from app.api import deps  # For get_db

router = APIRouter()


@router.post(
    "/register", response_model=schemas_user.User, status_code=status.HTTP_201_CREATED
)
def register_user(user_in: schemas_user.UserCreate, db: Session = Depends(deps.get_db)):
    """
    Create new user.
    """
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    created_user = crud_user.create_user(db=db, user=user_in)
    return created_user


@router.post("/token", response_model=schemas_token.Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username is the email.
    """
    user = crud_user.get_user_by_email(
        db, email=form_data.username
    )  # form_data.username is the email
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = security.create_access_token(
        data={"sub": user.email}  # 'sub' (subject) is the user's email
    )
    return {"access_token": access_token, "token_type": "bearer"}
