from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.contact import Contact, ContactCreate, ContactUpdate
from app.db.models.contact import Contact as ContactModel
from app.db.models.user import User as UserModel
from app.db.database import get_db
from sqlalchemy.orm import Session
from typing import List, Annotated
import uuid

# Import the authentication dependency
from app.api.v1.endpoints.access import get_current_user

router = APIRouter()

@router.get("/contacts", tags=["Emergencies"], response_model=List[Contact])
async def get_user_contacts(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get all contacts for the authenticated user"""
    contacts = db.query(ContactModel).filter(ContactModel.user_id == current_user.id).all()
    return contacts

@router.post("/contacts", tags=["Emergencies"], status_code=status.HTTP_201_CREATED, response_model=Contact)
async def create_contact(
    contact_data: ContactCreate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new emergency contact for the authenticated user"""
    # Create new contact associated with the current user
    new_contact = ContactModel(
        id=str(uuid.uuid4()),
        email=contact_data.email,
        name=contact_data.name if hasattr(contact_data, 'name') else None,
        phone=contact_data.phone if hasattr(contact_data, 'phone') else None,
        user_id=current_user.id  # Associate with current user automatically
    )
    
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    
    return new_contact

@router.put("/contacts/{contact_id}", tags=["Emergencies"], response_model=Contact)
async def update_contact(
    contact_id: str,
    contact_data: ContactUpdate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update a specific contact"""
    # Get the contact and verify it belongs to the current user
    contact = db.query(ContactModel).filter(
        ContactModel.id == contact_id,
        ContactModel.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or you don't have permission to modify it"
        )
    
    # Update contact fields
    for key, value in contact_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(contact, key, value)
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact

@router.delete("/contacts/{contact_id}", tags=["Emergencies"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Delete a specific contact"""
    # Get the contact and verify it belongs to the current user
    contact = db.query(ContactModel).filter(
        ContactModel.id == contact_id,
        ContactModel.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or you don't have permission to delete it"
        )
    
    # Delete the contact
    db.delete(contact)
    db.commit()
    
    return None