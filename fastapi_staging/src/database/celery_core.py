# # db_celery.py
#
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
# import os
# from dotenv import load_dotenv
#
# load_dotenv()
#
# # Original DATABASE_URL from .env
# DATABASE_URL = os.getenv("DATABASE_URL")
#
# # DO NOT change to async here — keep sync for Celery
# engine = create_engine(
#     DATABASE_URL,
#     pool_size=200,         # You can handle 200+ concurrent DB sessions
#     max_overflow=50,       # Extra burst connections if needed
#     pool_timeout=30,
#     pool_recycle=1800,
#     echo=False,
# )
#
# SessionLocal = scoped_session(sessionmaker(bind=engine))
# Base = declarative_base()
#
# # Dependency-like pattern for celery (not FastAPI)
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
#
# # Use Case
#
# # tasks.py
#
# # from celery import Celery
# # from db_celery import get_db
# # from models import MyModel
# #
# # celery_app = Celery(
# #     "worker",
# #     broker="redis://localhost:6379/0",
# #     backend="redis://localhost:6379/1",
# # )
# #
# # @celery_app.task
# # def process_records(task_id: str):
# #     db_gen = get_db()
# #     db = next(db_gen)
# #     try:
# #         records = db.query(MyModel).filter(MyModel.task_id == task_id).all()
# #         # Do something with records
# #     finally:
# #         db_gen.close()
#
#
# #Celery Concurrency Setup (CLI)
# # To support 200 concurrent workers:
# #
# # bash
# # Copy
# # Edit
# # celery -A tasks.celery_app worker --loglevel=info --concurrency=200
# # Or for thread-based concurrency (if tasks are I/O bound):
# #
# # bash
# # Copy
# # Edit
# # celery -A tasks.celery_app worker --pool=threads --concurrency=200
