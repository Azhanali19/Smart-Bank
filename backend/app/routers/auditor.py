from fastapi import APIRouter, Depends, HTTPException
from ..utils import get_current_user, log_audit

router = APIRouter(prefix="/auditor", tags=["auditor"])

@router.get("/audit-logs")
async def get_audit_logs(user=Depends(get_current_user)):
    if user.get("role") != "auditor":
        raise HTTPException(status_code=403, detail="Only auditors allowed")
    from ..database import audit_col
    cursor = audit_col.find({}).sort("timestamp", -1).limit(200)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        items.append(doc)
    await log_audit(user.get("sub"), "view_audit_logs")
    return items
