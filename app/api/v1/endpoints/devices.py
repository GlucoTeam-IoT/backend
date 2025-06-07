from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.schemas.device import Device, DeviceCreate, DeviceUpdate
from app.db.models.device import Device as DeviceModel, Status
from app.db.models.user import User as UserModel
from app.db.database import get_db
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
import uuid
from datetime import datetime

# Import the authentication dependency
from app.api.v1.endpoints.access import get_current_user

router = APIRouter()

@router.post("/devices", tags=["Devices"], status_code=status.HTTP_201_CREATED, response_model=Device)
async def create_device(
    device_data: DeviceCreate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new device for the authenticated user"""
    
    # Create new device with association to current user
    new_device = DeviceModel(
        id=str(uuid.uuid4()),
        status=Status.ACTIVE,
        timestamp=device_data.timestamp if hasattr(device_data, 'timestamp') else datetime.now(),
        user_id=current_user.id
    )
    
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    
    return new_device

@router.get("/devices", tags=["Devices"], response_model=List[Device])
async def get_user_devices(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    status: Optional[str] = Query(None, description="Filter by device status"),
    db: Session = Depends(get_db)
):
    """Get all devices for the authenticated user"""
    
    # Query all devices for the current user
    query = db.query(DeviceModel).filter(DeviceModel.user_id == current_user.id)
    
    # Apply status filter if provided
    if status:
        try:
            device_status = Status[status.upper()]
            query = query.filter(DeviceModel.status == device_status)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in Status])}"
            )
    
    # Order by most recent first
    query = query.order_by(DeviceModel.timestamp.desc())
    
    return query.all()

@router.get("/devices/{device_id}", tags=["Devices"], response_model=Device)
async def get_device(
    device_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get a specific device by ID"""
    
    # Get the device and verify it belongs to the current user
    device = db.query(DeviceModel).filter(
        DeviceModel.id == device_id,
        DeviceModel.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or you don't have access to it"
        )
        
    return device

@router.put("/devices/{device_id}", tags=["Devices"], response_model=Device)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update a device's status and information"""
    
    # Get the device and verify it belongs to the current user
    device = db.query(DeviceModel).filter(
        DeviceModel.id == device_id,
        DeviceModel.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or you don't have access to it"
        )
    
    # Update device fields
    if device_data.status is not None:
        device.status = device_data.status
    
    # Always update timestamp when device is modified
    device.timestamp = device_data.timestamp if device_data.timestamp else datetime.now()
    
    # Update record association if provided
    if device_data.record_id is not None:
        device.record_id = device_data.record_id
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return device

@router.delete("/devices/{device_id}", tags=["Devices"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Delete a device"""
    
    # Get the device and verify it belongs to the current user
    device = db.query(DeviceModel).filter(
        DeviceModel.id == device_id,
        DeviceModel.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or you don't have access to it"
        )
    
    # Delete the device
    db.delete(device)
    db.commit()
    
    return None