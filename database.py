import logging
from motor.motor_asyncio import AsyncIOMotorClient
import config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DATABASE_NAME]
        self.users = self.db["users"]
        self.payloads = self.db["payloads"]
        self.fsub_channels = self.db["fsub_channels"]

    async def add_user(self, user_id: int, first_name: str):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"first_name": first_name}},
            upsert=True
        )

    async def store_payload(self, payload_id: str, channel_id: int, message_id: int):
        await self.payloads.update_one(
            {"payload_id": payload_id},
            {"$set": {"channel_id": channel_id, "message_id": message_id}},
            upsert=True
        )

    async def get_payload(self, payload_id: str):
        return await self.payloads.find_one({"payload_id": payload_id})

    # Extra Force-Subscribe Channel Methods
    async def add_fsub_channel(self, channel_id: int):
        await self.fsub_channels.update_one(
            {"channel_id": channel_id},
            {"$set": {"channel_id": channel_id}},
            upsert=True
        )

    async def remove_fsub_channel(self, channel_id: int):
        await self.fsub_channels.delete_one({"channel_id": channel_id})

    async def get_fsub_channels(self):
        cursor = self.fsub_channels.find({})
        return [doc async for doc in cursor]

db = Database()
