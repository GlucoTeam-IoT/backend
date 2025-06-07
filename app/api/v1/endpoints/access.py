from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import ALGORITHM, SECRET_KEY, create_access_token, verify_password, get_password_hash
from app.schemas.user import UserSignUp, UserSignIn, User, UserUpdate
from app.db.models.user import User as UserModel
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import uuid
from datetime import timedelta
from jose import JWTError, jwt

security = HTTPBearer()

router = APIRouter()

def get_user_from_token(token: str, db: Session):
    """
    Decodes JWT token and returns the user from database
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        # Get user from database
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        return user
    except JWTError:
        return None

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get token from credentials
    token = credentials.credentials
    user = get_user_from_token(token, db)
    if user is None:
        raise credentials_exception
    return user

@router.post("/users/sign-up", tags=["Access"], status_code=status.HTTP_201_CREATED, response_model=User)
async def sign_up_user(user_data: UserSignUp, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user with this email already exists
    existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user_data.password)

    # Create new user
    new_user = UserModel(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/users/sign-in", tags=["Access"])
async def sign_in_user(credentials: UserSignIn, db: Session = Depends(get_db)):
    """Login and returns a JWT"""
    # Find user by email
    user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/get-information", tags=["Access"], response_model=User)
async def get_user_information(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Gets the information of the current user"""
    return current_user

@router.put("/users/update-information", tags=["Access"], response_model=User)
async def update_user_information(    
    user_data: UserUpdate, 
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)):
    """Update user information"""
    user = current_user
    
    for key, value in user_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, key, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)

    return user