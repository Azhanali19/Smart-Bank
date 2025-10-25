from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from ..utils import get_current_user, log_audit
from .. import crud
from ..schemas import TransactionCreate, LoanApply
from bson import ObjectId
from ..database import accounts_col, transactions_col, loans_col
from datetime import datetime, timedelta

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("/me/account")
async def my_account(user=Depends(get_current_user)):
    """Return the authenticated customer's account."""
    user_id = user.get("sub")
    acc = await crud.get_account_by_user(user_id)
    await log_audit(user_id, "view_account")
    if not acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return acc

@router.post("/transactions")
async def perform_transaction(tx: TransactionCreate, user=Depends(get_current_user)):
    """Handle deposit, withdraw and transfer in a safe way (basic checks).

    Note: For true cross-account atomicity you'd need MongoDB transactions (replica set).
    This implementation uses conditional updates to reduce race conditions for withdrawals.
    """
    actor_id = user.get("sub")
    amount = float(tx.amount)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Deposit: increase to_account
    if tx.type == "deposit":
        if not tx.to_account:
            raise HTTPException(status_code=400, detail="to_account is required for deposit")
        # update and return the updated account
        res = await accounts_col.find_one_and_update(
            {"_id": ObjectId(tx.to_account)},
            {"$inc": {"balance": amount}},
            return_document=True
        )
        if not res:
            raise HTTPException(status_code=404, detail="Destination account not found")
        tx_db = await crud.create_transaction({**tx.dict(), "performed_by": actor_id})
        await log_audit(actor_id, "deposit", {"to": tx.to_account, "amount": amount})
        res["id"] = str(res["_id"])
        return {"tx": tx_db, "to_account": res}

    # Withdraw: decrease from_account only if sufficient balance
    if tx.type == "withdraw":
        if not tx.from_account:
            raise HTTPException(status_code=400, detail="from_account is required for withdraw")
        # conditional update to ensure balance doesn't go negative
        updated = await accounts_col.find_one_and_update(
            {"_id": ObjectId(tx.from_account), "balance": {"$gte": amount}},
            {"$inc": {"balance": -amount}},
            return_document=True
        )
        if not updated:
            raise HTTPException(status_code=400, detail="Insufficient balance or account not found")
        tx_db = await crud.create_transaction({**tx.dict(), "performed_by": actor_id})
        await log_audit(actor_id, "withdraw", {"from": tx.from_account, "amount": amount})
        updated["id"] = str(updated["_id"])
        return {"tx": tx_db, "from_account": updated}

    # Transfer: try conditional deduction then credit. Not fully atomic without transactions.
    if tx.type == "transfer":
        if not tx.from_account or not tx.to_account:
            raise HTTPException(status_code=400, detail="from_account and to_account are required for transfer")
        # 1) deduct from source if it has enough balance
        deducted = await accounts_col.find_one_and_update(
            {"_id": ObjectId(tx.from_account), "balance": {"$gte": amount}},
            {"$inc": {"balance": -amount}},
            return_document=True
        )
        if not deducted:
            raise HTTPException(status_code=400, detail="Insufficient balance or from_account not found")
        # 2) credit destination
        credited = await accounts_col.find_one_and_update(
            {"_id": ObjectId(tx.to_account)},
            {"$inc": {"balance": amount}},
            return_document=True
        )
        if not credited:
            # Attempt to rollback deduction (best-effort) if destination missing
            await accounts_col.update_one({"_id": ObjectId(tx.from_account)}, {"$inc": {"balance": amount}})
            raise HTTPException(status_code=404, detail="Destination account not found — rolled back")

        tx_db = await crud.create_transaction({**tx.dict(), "performed_by": actor_id})
        await log_audit(actor_id, "transfer", {"from": tx.from_account, "to": tx.to_account, "amount": amount})
        deducted["id"] = str(deducted["_id"])
        credited["id"] = str(credited["_id"])
        return {"tx": tx_db, "from_account": deducted, "to_account": credited}

    raise HTTPException(status_code=400, detail="Unknown transaction type")

@router.post("/loans")
async def apply_loan(loan: LoanApply, user=Depends(get_current_user)):
    """Customer applies for a loan. Loan is created with `pending` status."""
    actor_id = user.get("sub")
    loan_data = loan.dict()
    # ensure the loan is tied to the authenticated user
    loan_data["user_id"] = actor_id
    loan_db = await crud.apply_loan(loan_data)
    await log_audit(actor_id, "apply_loan", {"loan_id": loan_db.get("id"), "amount": loan_db.get("amount")})
    return loan_db

@router.get("/loans")
async def my_loans(user=Depends(get_current_user)):
    actor_id = user.get("sub")
    cursor = loans_col.find({"user_id": actor_id}).sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        items.append(doc)
    await log_audit(actor_id, "view_loans")
    return items

@router.get("/statements")
async def statements(start_date: Optional[str] = None, end_date: Optional[str] = None, user=Depends(get_current_user)):
    """Get transaction statements for the authenticated user. Dates are ISO `YYYY-MM-DD` strings.

    Example: /customers/statements?start_date=2025-10-01&end_date=2025-10-25
    """
    actor_id = user.get("sub")
    # find customer's account id
    account = await accounts_col.find_one({"user_id": actor_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account_id = str(account["_id"])  # transactions store account object ids as strings in this app

    query = {"$or": [{"from_account": account_id}, {"to_account": account_id}]}
    # parse dates if provided
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except Exception:
            raise HTTPException(status_code=400, detail="start_date must be YYYY-MM-DD")
        query.setdefault("created_at", {})["$gte"] = start
    if end_date:
        try:
            # include the end date full day
            end = datetime.fromisoformat(end_date) + timedelta(days=1)
        except Exception:
            raise HTTPException(status_code=400, detail="end_date must be YYYY-MM-DD")
        query.setdefault("created_at", {})["$lt"] = end

    cursor = transactions_col.find(query).sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        items.append(doc)
    await log_audit(actor_id, "view_statements", {"count": len(items)})
    return items