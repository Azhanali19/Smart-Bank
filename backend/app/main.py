from fastapi import FastAPI
from .routers import auth, customers, admin, auditor, dashboard
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Banking App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

from app.routers import auth, customers, admin, auditor, dashboard

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(admin.router)
app.include_router(auditor.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"msg": "Banking app backend up."}