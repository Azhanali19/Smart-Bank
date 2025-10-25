from fastapi import APIRouter, Depends, HTTPException
from ..utils import get_current_user, log_audit, role_required
from .. import crud
from bson import ObjectId

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/loans/{loan_id}/approve")
async def approve(loan_id: str, user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve loans")
    res = await crud.approve_loan(loan_id, user.get("sub"))
    await log_audit(user.get("sub"), "approve_loan", {"loan_id": loan_id})
    return {"loan": res}

@router.get("/flagged-transactions")
async def flagged_transactions(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403)
    from ..database import transactions_col
    cursor = transactions_col.find({"flagged": True})
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        items.append(doc)
    await log_audit(user.get("sub"), "view_flagged_transactions")
    return items

@router.get("/accounts")
async def list_accounts(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403)
    from ..database import accounts_col
    cursor = accounts_col.find({})
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        items.append(doc)
    await log_audit(user.get("sub"), "list_accounts")
    return items