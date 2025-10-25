from .database import users_col, accounts_col, transactions_col, loans_col
from .utils import hash_password, verify_password
from bson import ObjectId
from datetime import datetime

async def create_user(user_data: dict):
    existing = await users_col.find_one({"email": user_data["email"]})
    if existing:
        return None
    user = {
        "email": user_data["email"],
        "password": hash_password(user_data["password"]),
        "full_name": user_data.get("full_name"),
        "role": user_data.get("role", "customer"),
        "created_at": datetime.utcnow()
    }
    res = await users_col.insert_one(user)
    user_id = str(res.inserted_id)
    # create account
    account = {"user_id": user_id, "balance": 0.0, "currency": "INR", "created_at": datetime.utcnow()}
    await accounts_col.insert_one(account)
    return {"id": user_id, "email": user["email"], "full_name": user["full_name"], "role": user["role"]}

async def authenticate_user(email: str, password: str):
    user = await users_col.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    user["id"] = str(user["_id"])
    return user

async def get_account_by_user(user_id: str):
    acc = await accounts_col.find_one({"user_id": user_id})
    if not acc:
        return None
    acc["id"] = str(acc["_id"])
    return acc

async def create_transaction(tx: dict):
    tx_db = tx.copy()
    tx_db.update({"created_at": datetime.utcnow()})
    res = await transactions_col.insert_one(tx_db)
    tx_db["id"] = str(res.inserted_id)
    return tx_db

async def update_balance(account_id: str, amount_change: float):
    res = await accounts_col.find_one_and_update(
        {"_id": ObjectId(account_id)},
        {"$inc": {"balance": amount_change}},
        return_document=True
    )
    return res

async def apply_loan(loan: dict):
    loan_db = loan.copy()
    loan_db.update({"status": "pending", "created_at": datetime.utcnow()})
    res = await loans_col.insert_one(loan_db)
    loan_db["id"] = str(res.inserted_id)
    return loan_db

async def approve_loan(loan_id: str, admin_id: str):
    res = await loans_col.find_one_and_update(
        {"_id": ObjectId(loan_id)},
        {"$set": {"status": "approved", "approved_by": admin_id, "approved_at": datetime.utcnow()}},
        return_document=True
    )
    return res