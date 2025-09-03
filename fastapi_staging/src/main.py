import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .database.core import engine, Base
from .entities.todo import Todo
from .entities.user import User
from .api import register_routes
# from .logging import configure_logging, LogLevels

# configure_logging(LogLevels.info)

# Optional: read root path from env (useful if mounted under /api by proxy)
root_path = os.getenv("FASTAPI_ROOT_PATH", "")

app = FastAPI(
    title="Still Missed Children (SMC) API",
    docs_url="/docs",           # was /api/docs
    redoc_url="/redoc",         # was /api/redoc
    openapi_url="/openapi.json" # was /api/openapi.json
)

router = APIRouter()

@router.get("/")
async def api_root():
    return {"message": "API base"}

@router.get("/health")
async def health():
    return {"status": "ok"}

# Attach the router to the app (no /api prefix anymore)
app.include_router(router)

# Updated CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://smcv2.eoc.gov.pk",   # frontend / production
        "http://localhost:8000",      # local dev
        "http://192.168.2.232:8000",  # dev IP
        "http://172.16.3.132:8001",   # direct FastAPI
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" Only uncomment below to create new tables, 
otherwise the pytest will fail if not connected
"""
# Base.metadata.create_all(bind=engine)

register_routes(app)
