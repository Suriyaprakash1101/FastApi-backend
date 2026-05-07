

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.Schemas.userSchema import UserBase, UserCreate, UserResponse, UserLogin
from app.Schemas.tokenSchema import Token, RefreshTokenRequest
from ...database import get_db
from app.utils.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, get_current_user_id,
    get_current_user
)
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, name=user.name, password=hashed_password, address=user.address,mobile = user.mobile)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User could not be created")


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    # Hard delete old tokens to keep only one record per user
    db.query(RefreshToken).filter(RefreshToken.user_id == db_user.id).delete()

    refresh_token_expiry = datetime.utcnow() + timedelta(days=7)
    db_refresh_token = RefreshToken(user_id=db_user.id, token=refresh_token, expires_at=refresh_token_expiry)
    db.add(db_refresh_token)
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token,
        RefreshToken.user_id == UUID(user_id),
        RefreshToken.revoked.is_(None)
    ).first()

    if not db_refresh_token or db_refresh_token.is_expired():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

    # Hard delete old token
    db.delete(db_refresh_token)

    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})

    new_db_refresh_token = RefreshToken(
        user_id=UUID(user_id),
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(new_db_refresh_token)
    db.commit()

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    db_refresh_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if db_refresh_token:
        db.delete(db_refresh_token)
        db.commit()
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_my_profile(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")

    token = authorization.split(" ")[1]
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user





@router.patch("/me/update", response_model=UserResponse)
def patch_current_user(
    user_update: UserBase,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)  # <-- clean auth
):
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updates = user_update.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    for key, value in updates.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=list[UserResponse])
def get_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# @router.put("/{user_id}", response_model=UserResponse)
# def update_user(authorization:Option[str]=Header(None),user_id: str, user_update: UserBase, db: Session = Depends(get_db)):
#     try:
#         user_uuid = UUID(user_id)
#     except ValueError:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

#     user = db.query(User).filter(User.id == user_uuid).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     for key, value in user_update.model_dump().items():
#         setattr(user, key, value)

#     db.commit()
#     db.refresh(user)
#     return user


@router.put("/update/{user_id}", response_model=UserResponse)
def update_user(
    
    user_id: str, 
    user_update: UserBase, 
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # Validate authentication
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    
    try:
        token = authorization.split(" ")[1]
        current_user_id = get_current_user_id(token)
    except IndexError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization format. Use 'Bearer <token>'")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    # Validate user_id UUID format
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    
    # Find user to update
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check permission: users can only update their own profile
    if current_user_id != user_uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    
    # Update user fields
    for key, value in user_update.model_dump().items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.query(RefreshToken).filter(RefreshToken.user_id == user_uuid).delete()
    db.delete(user)
    db.commit()
    return None