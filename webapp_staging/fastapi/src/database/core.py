from typing import AsyncGenerator
from typing_extensions import Annotated
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import Depends
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Update the DB URL to asyncpg format
# Example: "postgresql+asyncpg://user:pass@host:port/db"
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# ✅ Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=100, max_overflow=200)

# ✅ Create async session factory
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# ✅ Declarative base
Base = declarative_base()

# ✅ Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# ✅ Alias for FastAPI DI
DbSession = Annotated[AsyncSession, Depends(get_db)]
