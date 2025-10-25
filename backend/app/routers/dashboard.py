from fastapi import APIRouter, Depends
from ..utils import get_current_user, log_audit
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
async def dashboard_summary(user=Depends(get_current_user)):
    # For admin or customer
    from ..database import accounts_col, transactions_col, loans_col
    uid = user.get("sub")
    # account summary
    if user.get("role") == "customer":
        acc = await accounts_col.find_one({"user_id": uid})
        acc_summary = {"balance": acc.get("balance", 0)} if acc else {}
    else:
        # admin sees totals
        pipeline = [{"$group": {"_id": None, "total_balance": {"$sum": "$balance"}}}]
        res = await accounts_col.aggregate(pipeline).to_list(length=1)
        acc_summary = res[0] if res else {"total_balance": 0}

    # simple transaction trends: count per day for last 7 days
    since = datetime.utcnow() - timedelta(days=7)
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "count": {"$sum": 1}, "total": {"$sum": "$amount"}}},
        {"$sort": {"_id": 1}}
    ]
    trends = await transactions_col.aggregate(pipeline).to_list(length=30)

    # loan repayment status: counts by status
    loan_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    loan_stats = await loans_col.aggregate(loan_pipeline).to_list(length=10)

    await log_audit(user.get("sub"), "view_dashboard")
    return {"account_summary": acc_summary, "transaction_trends": trends, "loan_repayment_status": loan_stats}