from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]

# Collections
users_col = db["users"]
accounts_col = db["accounts"]
transactions_col = db["transactions"]
loans_col = db["loans"]
audit_col = db["audit_logs"]