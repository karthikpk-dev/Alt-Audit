from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from ..database import get_db
from .. import auth, schemas, models
from ..config import settings
from ..dependencies import get_current_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])

# All dependencies imported from dependencies.py


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user: User registration data
        db: Database session
        
    Returns:
        UserResponse: The created user data
        
    Raises:
        HTTPException: If email or username already exists
    """
    try:
        db_user = auth.create_user(db, user)
        return schemas.UserResponse.from_orm(db_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login-json", response_model=schemas.Token)
async def login_user_json(
    user_credentials: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with JSON payload and return access token.
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        Token: Access token and metadata
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = auth.authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user data
    """
    return schemas.UserResponse.from_orm(current_user)


@router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    
    Args:
        user_update: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user data
        
    Raises:
        HTTPException: If email or username already exists
    """
    try:
        updated_user = auth.update_user(db, current_user.id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return schemas.UserResponse.from_orm(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_current_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Deactivate current user account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        None
        
    Raises:
        HTTPException: If user not found
    """
    success = auth.deactivate_user(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    """
    Refresh access token for current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token: New access token and metadata
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


# All dependencies are imported at the top of the file
