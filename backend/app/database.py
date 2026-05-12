"""
Database configuration and session management using Motor and Beanie
"""
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorClient
# pyrefly: ignore [missing-import]
from beanie import init_beanie
from app.config import settings
import app.models as models

# We will initialize this in main.py startup event
client = None

async def init_db():
    """Initialize database and Beanie models"""
    global client
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    
    # Initialize Beanie with the Motor client
    # We pass all the Document models here
    await init_beanie(
        database=client.get_default_database(),
        document_models=[
            models.User,
            models.Instance,
            models.Alert,
            models.AlertConfig,
            models.MetricsSnapshot
        ]
    )

def get_db():
    """Dependency for getting database session.
    With Beanie, this is largely unneeded, but kept for compatibility 
    if any route still expects a dependency, though it can yield None.
    """
    yield None
