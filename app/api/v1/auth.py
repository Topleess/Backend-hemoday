"""
Authentication endpoints - register, login, join family
"""
from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas import (
    UserRegister,
    UserLogin,
    JoinFamily,
    Token,
    UserResponse,
    PasswordResetRequest,
    PasswordResetResponse,
)
from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.family import Family
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from fastapi import Depends


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister):
    """
    Register new user and auto-create a family
    """
    # Check if user already exists
    existing_user = await User.filter(email=data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create family (without patient data for now)
    family = await Family.create()
    
    # Create user
    password_hash = get_password_hash(data.password)
    user = await User.create(
        email=data.email,
        password_hash=password_hash,
        family_id=family.id,
    )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user_id=str(user.id),
        family_id=str(family.id),
        invite_code=family.invite_code,
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    """
    Login user with email and password
    """
    # Find user
    user = await User.filter(email=data.email).prefetch_related("family").first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is deleted
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account has been deleted"
        )
    
    # Verify password
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user_id=str(user.id),
        family_id=str(user.family_id),
        invite_code=user.family.invite_code,
    )


@router.post("/join-family", response_model=Token, status_code=status.HTTP_201_CREATED)
async def join_family(data: JoinFamily):
    """
    Join existing family using invite code
    """
    # Check if user already exists
    existing_user = await User.filter(email=data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Find family by invite code
    family = await Family.filter(invite_code=data.invite_code.upper()).first()
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code"
        )
    
    # Create user
    password_hash = get_password_hash(data.password)
    user = await User.create(
        email=data.email,
        password_hash=password_hash,
        family_id=family.id,
    )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user_id=str(user.id),
        family_id=str(family.id),
        invite_code=family.invite_code,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        family_id=current_user.family_id,
        created_at=current_user.created_at,
    )


@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(data: PasswordResetRequest):
    """
    Request password reset - sends email with new temporary password
    """
    # Find user by email
    user = await User.filter(email=data.email).first()
    if not user:
        # Return success even if user not found (security best practice)
        return PasswordResetResponse(
            message="If this email exists in our system, a password reset email will be sent."
        )
    
    # Check if user is deleted
    if user.deleted_at is not None:
        return PasswordResetResponse(
            message="If this email exists in our system, a password reset email will be sent."
        )
    
    # Generate new temporary password
    import secrets
    import string
    temporary_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    # Update user password
    user.password_hash = get_password_hash(temporary_password)
    await user.save()
    
    # TODO: Send email with temporary password
    # For now, we'll just log it (in production, send actual email)
    print(f"Password reset for {user.email}: {temporary_password}")
    
    # Create reset token for tracking
    await PasswordResetToken.create_token(user.id)
    
    return PasswordResetResponse(
        message="If this email exists in our system, a password reset email will be sent."
    )
