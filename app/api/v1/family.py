from fastapi import APIRouter, HTTPException, status, Depends
from app.models.family import Family
from app.models.user import User
from app.api.v1.schemas import Token, JoinFamilyRequest, FamilyDetailsResponse, RemoveMemberRequest, UserResponse
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from typing import List

router = APIRouter(prefix="/family", tags=["Family"])

@router.post("/join", response_model=Token)
async def join_family(
    data: JoinFamilyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Join an existing family using invite code (for logged in users)
    """
    await current_user.fetch_related("family")
    
    # Check if user is already in a family with members or is an owner
    family_members_count = await User.filter(family_id=current_user.family_id).count()
    is_owner = current_user.family.owner_id == str(current_user.id)
    
    if family_members_count > 1:
        if is_owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot join another family while you have members in your current family. Remove them or leave first."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must leave your current family before joining a new one."
            )

    # Find family by invite code
    family = await Family.filter(invite_code=data.invite_code.upper()).first()
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code"
        )
    
    # Update user's family
    current_user.family_id = family.id
    await current_user.save()
    
    # Generate new token (optional, but good practice if token contains family_id claims)
    access_token = create_access_token(data={"sub": str(current_user.id)})
    
    return Token(
        access_token=access_token,
        user_id=str(current_user.id),
        family_id=str(family.id),
        invite_code=family.invite_code,
    )
@router.get("/", response_model=FamilyDetailsResponse)
async def get_family_details(current_user: User = Depends(get_current_user)):
    """
    Get current family details and members
    """
    await current_user.fetch_related("family")
    family = current_user.family
    
    # Get all members
    members = await User.filter(family_id=family.id).all()
    
    member_responses = [
        UserResponse(
            id=m.id,
            email=m.email,
            family_id=m.family_id,
            invite_code=family.invite_code,
            created_at=m.created_at
        )
        for m in members
    ]
    
    return FamilyDetailsResponse(
        id=family.id,
        invite_code=family.invite_code,
        owner_id=family.owner_id,
        patient_name=family.patient_name,
        patient_current_weight=family.patient_current_weight,
        patient_birth_date=family.patient_birth_date,
        members=member_responses
    )


@router.post("/leave", response_model=Token)
async def leave_family(current_user: User = Depends(get_current_user)):
    """
    Leave current family and create a new individual one
    """
    await current_user.fetch_related("family")
    family_members_count = await User.filter(family_id=current_user.family_id).count()
    is_owner = current_user.family.owner_id == str(current_user.id)
    
    if is_owner and family_members_count > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As the family owner, you cannot leave while there are other members. Remove them first or hand over ownership (not supported)."
        )

    # Create new family for the user
    new_family = await Family.create(owner_id=str(current_user.id))
    
    current_user.family_id = new_family.id
    await current_user.save()
    
    # Generate new token
    access_token = create_access_token(data={"sub": str(current_user.id)})
    
    return Token(
        access_token=access_token,
        user_id=str(current_user.id),
        family_id=str(new_family.id),
        invite_code=new_family.invite_code,
    )


@router.post("/remove-member", response_model=FamilyDetailsResponse)
async def remove_member(
    data: RemoveMemberRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a member from the family (moves them to their own new family)
    """
    # Check if target user is in the same family
    target_user = await User.filter(id=data.user_id, family_id=current_user.family_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in your family"
        )
    
    if str(target_user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself. Use /leave instead."
        )
    
    # Verify ownership
    await current_user.fetch_related("family")
    if current_user.family.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the family owner can remove members"
        )
        
    # Create new family for the removed user
    new_family = await Family.create(owner_id=str(target_user.id))
    target_user.family_id = new_family.id
    await target_user.save()
    
    # Return updated family details
    return await get_family_details(current_user)
