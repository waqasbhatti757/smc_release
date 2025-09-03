from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SMC FastAPI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SMC FastAPI Service is running"}

@app.get("/api/")
async def api_root():
    return {"message": "API endpoint working", "endpoints": ["/docs", "/api/"]}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "smc-fastapi"}

@app.get("/api/users")
async def get_users():
    return {"users": ["user1", "user2", "user3"]}

@app.get("/api/campaigns")
async def get_campaigns():
    return {"campaigns": ["campaign1", "campaign2"]}

@app.get("/api/auth/login")
async def login():
    return {"message": "Login endpoint"}

@app.get("/api/auth/register")
async def register():
    return {"message": "Register endpoint"}
