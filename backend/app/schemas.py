from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "customer"  # customer | admin | auditor

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str

class Login(BaseModel):
    email: EmailStr
    password: str

class Account(BaseModel):
    id: Optional[str]
    user_id: str
    balance: float = 0.0
    currency: str = "INR"

class TransactionCreate(BaseModel):
    from_account: Optional[str]
    to_account: Optional[str]
    amount: float
    type: str  # deposit, withdraw, transfer
    note: Optional[str] = None

class TransactionOut(BaseModel):
    id: str
    from_account: Optional[str]
    to_account: Optional[str]
    amount: float
    type: str
    created_at: datetime

class LoanApply(BaseModel):
    user_id: str
    amount: float
    term_months: int
    reason: Optional[str]

class LoanOut(BaseModel):
    id: str
    user_id: str
    amount: float
    term_months: int
    status: str
    created_at: datetime

class DashboardResponse(BaseModel):
    account_summary: dict
    transaction_trends: List[dict]
    loan_repayment_status: List[dict]