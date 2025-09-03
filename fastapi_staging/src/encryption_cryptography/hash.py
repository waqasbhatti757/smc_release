import asyncio
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
load_dotenv()
SALT = os.getenv("PASSWORD_SALT")
PREFIX = "!@#$%^&*()"
SUFFIX = "()&*^%$#@!"

async def style_password(password: str) -> str:
    """Wrap password with fixed symbols."""
    return f"{PREFIX}{password}{SUFFIX}"


async def create_password_hash(password: str) -> str:
    """Create deterministic hash using cryptography."""
    styled = await style_password(password)
    digest = hashes.Hash(hashes.SHA256())
    digest.update((SALT + styled).encode())
    return digest.finalize().hex()


async def verify_password_hash(password: str, given_hash: str) -> bool:
    """Verify if the given password matches the given hash."""
    generated_hash = await create_password_hash(password)
    return generated_hash == given_hash

#
#
# async def bulk_update_passwords(db: AsyncSession) -> int:
#     """
#     Fetch all users with final_password, generate hash + style,
#     update them in the DB.
#     Returns the count of updated users.
#     """
#     # 1. Get all users with final_password
#     query = text("""
#         SELECT username, final_password
#         FROM users
#         WHERE final_password IS NOT NULL
#     """)
#     result = await db.execute(query)
#     users = result.fetchall()
#
#     if not users:
#         return 0
#
#     # 2. Process each user and update
#     for user_id, final_password in users:
#         styled = await style_password(final_password)
#         hashed = await create_password_hash(final_password)
#
#         update_q = text("""
#             UPDATE users
#             SET password_style_de_passe = :styled,
#                 password_hash = :hashed
#             WHERE username = :id
#         """)
#         await db.execute(update_q, {"styled": styled, "hashed": hashed, "id": user_id})
#
#     # 3. Commit once
#     await db.commit()
#     return len(users)
#
#
# DATABASE_URL = "postgresql+asyncpg://postgres:testuser@localhost:5436/smc_staging"
#
#
# async def main():
#     engine = create_async_engine(DATABASE_URL, echo=False)
#     async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
#
#     async with async_session() as session:
#         count = await bulk_update_passwords(session)
#         print(f"✅ Updated {count} users")
#
# if __name__ == "__main__":
#     asyncio.run(main())
