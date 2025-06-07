from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.schemas.record import Record, RecordCreate
from app.db.models.record import Record as RecordModel
from app.db.models.device import Device as DeviceModel
from app.db.models.user import User as UserModel
from app.db.database import get_db
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
import uuid
from datetime import datetime

# Import the authentication dependency
from app.api.v1.endpoints.access import get_current_user

router = APIRouter()

@router.post("/records", tags=["Records"], status_code=status.HTTP_201_CREATED, response_model=Record)
async def create_record(
    record_data: RecordCreate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new glucose level record for the authenticated user"""
    
    # Verify device belongs to user if device_id is provided
    if record_data.device_id:
        device = db.query(DeviceModel).filter(
            DeviceModel.id == record_data.device_id,
            DeviceModel.user_id == current_user.id
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found or you don't have access to it"
            )
    
    # Create new record
    new_record = RecordModel(
        id=str(uuid.uuid4()),
        level=record_data.level,
        description=record_data.description,
        timestamp=record_data.timestamp if record_data.timestamp else datetime.now(),
        user_id=current_user.id,
        device_id=record_data.device_id
    )
    
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return new_record

@router.get("/records", tags=["Records"], response_model=List[Record])
async def get_user_records(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    limit: int = Query(100, description="Maximum number of records to return"),
    skip: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get all glucose level records for the authenticated user"""
    
    records = db.query(RecordModel)\
                .filter(RecordModel.user_id == current_user.id)\
                .order_by(RecordModel.timestamp.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()
    
    return records

@router.get("/records/device/{device_id}", tags=["Records"], response_model=List[Record])
async def get_device_records(
    device_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    limit: int = Query(100, description="Maximum number of records to return"),
    skip: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get all glucose level records for a specific device"""
    
    # Verify device belongs to user
    device = db.query(DeviceModel).filter(
        DeviceModel.id == device_id,
        DeviceModel.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or you don't have access to it"
        )
    
    records = db.query(RecordModel)\
                .filter(RecordModel.device_id == device_id)\
                .order_by(RecordModel.timestamp.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()
    
    return records

@router.get("/records/{record_id}", tags=["Records"], response_model=Record)
async def get_record(
    record_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get a specific glucose level record by ID"""
    
    record = db.query(RecordModel).filter(
        RecordModel.id == record_id,
        RecordModel.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found or you don't have access to it"
        )
        
    return record

@router.delete("/records/{record_id}", tags=["Records"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Delete a specific glucose level record"""
    
    record = db.query(RecordModel).filter(
        RecordModel.id == record_id,
        RecordModel.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found or you don't have access to it"
        )
    
    db.delete(record)
    db.commit()
    
    return None