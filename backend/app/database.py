from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import InventoryItem, Recipe, ChatMessage
import os

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "despensa")

# Global client
client = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM"""
    global client

    # Create Motor client
    client = AsyncIOMotorClient(MONGODB_URL)

    # Initialize Beanie with Document models
    await init_beanie(
        database=client[MONGODB_DB_NAME],
        document_models=[
            InventoryItem,
            Recipe,
            ChatMessage
        ]
    )

    print(f"✅ Connected to MongoDB: {MONGODB_URL}/{MONGODB_DB_NAME}")


async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")


# Helper function to get database
def get_database():
    """Get MongoDB database instance"""
    global client
    if not client:
        raise Exception("Database not initialized. Call init_db() first.")
    return client[MONGODB_DB_NAME]
