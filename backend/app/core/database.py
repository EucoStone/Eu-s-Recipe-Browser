from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


client: AsyncIOMotorClient | None = None


def get_database() -> AsyncIOMotorDatabase:
    if client is None:
        raise RuntimeError("MongoDB client is not initialized.")
    return client[get_settings().mongo_db]


async def init_db() -> None:
    global client
    cfg = get_settings()
    client = AsyncIOMotorClient(cfg.mongo_uri)
    db = client[cfg.mongo_db]
    await db.recipes.create_index("recipe_id", unique=True)
    await db.recipes.create_index("outputs")
    await db.recipes.create_index("output_name")
    await db.recipes.create_index([("raw.output", "text"), ("raw.result", "text"), ("raw.item", "text")])


async def close_db() -> None:
    global client
    if client is not None:
        client.close()
        client = None
