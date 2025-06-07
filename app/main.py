import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and models
from app.db.database import engine, Base

from app.db.models.user import User
from app.db.models.contact import Contact
from app.db.models.device import Device
from app.db.models.record import Record
from app.db.models.alert import Alert

# Uncomment this line to drop all tables
# Base.metadata.drop_all(bind=engine) 

# Create all tables
Base.metadata.create_all(bind=engine)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as api_router

# Create FastAPI app with metadata
app = FastAPI(
    title="GlucoTeam API",
    description="API for glucose monitoring application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

#CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "environment": os.getenv("ENVIRONMENT", "development")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)