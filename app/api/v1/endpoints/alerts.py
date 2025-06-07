from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.schemas.alert import Alert, AlertCreate, AlertBase
from app.db.models.alert import Alert as AlertModel, AlertLevel
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

@router.post("/alerts", tags=["Alerts"], status_code=status.HTTP_201_CREATED, response_model=Alert)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new alert from a device reading.
    This endpoint should be called by IoT devices when glucose levels are abnormal.
    """
    # Verify the device exists
    device = db.query(DeviceModel).filter(DeviceModel.id == alert_data.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Create new alert
    new_alert = AlertModel(
        id=str(uuid.uuid4()),
        message=alert_data.message if hasattr(alert_data, 'message') else "Abnormal glucose levels detected",
        level=alert_data.level if hasattr(alert_data, 'level') else AlertLevel.CRITICAL,
        timestamp=datetime.now(),
        device_id=alert_data.device_id
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    return new_alert

@router.get("/alerts", tags=["Alerts"], response_model=List[Alert])
async def get_alerts(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    level: Optional[str] = Query(None, description="Filter by alert level"),
    limit: int = Query(100, description="Maximum number of alerts to return"),
    skip: int = Query(0, description="Number of alerts to skip"),
    db: Session = Depends(get_db)
):
    """
    Get all alerts for the current user's devices.
    Can be filtered by device ID and alert level.
    """
    # Get all devices associated with this user
    user_devices = db.query(DeviceModel).filter(DeviceModel.user_id == current_user.id).all()
    device_ids = [device.id for device in user_devices]
    
    if not device_ids:
        return []
    
    # Base query - get alerts for any of the user's devices
    query = db.query(AlertModel).filter(AlertModel.device_id.in_(device_ids))
    
    # Apply additional filters if provided
    if device_id:
        if device_id not in device_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this device"
            )
        query = query.filter(AlertModel.device_id == device_id)
        
    if level:
        try:
            alert_level = AlertLevel[level.upper()]
            query = query.filter(AlertModel.level == alert_level)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid alert level. Must be one of: {', '.join([l.value for l in AlertLevel])}"
            )
    
    # Order by most recent first and apply pagination
    query = query.order_by(AlertModel.timestamp.desc()).offset(skip).limit(limit)
    
    return query.all()

@router.get("/alerts/{alert_id}", tags=["Alerts"], response_model=Alert)
async def get_alert(
    alert_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get a specific alert by ID"""
    # Get all devices associated with this user
    user_devices = db.query(DeviceModel).filter(DeviceModel.user_id == current_user.id).all()
    device_ids = [device.id for device in user_devices]
    
    # Get the alert and verify it belongs to one of the user's devices
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
        
    if alert.device_id not in device_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this alert"
        )
        
    return alert

@router.delete("/alerts/{alert_id}", tags=["Alerts"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Delete a specific alert"""
    # Get all devices associated with this user
    user_devices = db.query(DeviceModel).filter(DeviceModel.user_id == current_user.id).all()
    device_ids = [device.id for device in user_devices]
    
    # Get the alert and verify it belongs to one of the user's devices
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
        
    if alert.device_id not in device_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this alert"
        )
    
    # Delete the alert
    db.delete(alert)
    db.commit()
    
    return None