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

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "smc-fastapi"}

@app.get("/api/test")
async def test_api():
    return {"message": "API endpoint working"}
