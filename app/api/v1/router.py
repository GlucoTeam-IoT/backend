from fastapi import APIRouter
from app.api.v1.endpoints import access, emergencies, alerts, devices, records

router = APIRouter(prefix="/api/v1")

router.include_router(access.router, tags=["Access"])
router.include_router(emergencies.router, tags=["Emergencies"])
router.include_router(records.router, tags=["Records"])
router.include_router(devices.router, tags=["Devices"])
router.include_router(alerts.router, tags=["Alerts"])