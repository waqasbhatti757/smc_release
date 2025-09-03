# from src.celery_main import celery_app
# from src.auth.models import TokenData
# from ..database.core import DbSession
# from src.exceptions import TodoCreationError, TodoNotFoundError
# import logging
# from . import service
# # from src.database.core import SessionLocal  # ✅ Manual session
# from ..auth.service import CurrentUser
#
# from datetime import datetime, timezone
# from uuid import uuid4, UUID
# from sqlalchemy.orm import Session
# from fastapi import HTTPException
# from . import models
# import time
# @celery_app.task(name="src.todos.celery_tasks.create_todo_task")  # 👈 must match
# def create_todo_task(todo_data: dict, user_id):
#     db = SessionLocal()  # create real session
#     try:
#         current_user = TokenData(user_id=user_id)
#         todo_model = models.TodoCreate(**todo_data)
#         service.create_todo(current_user, db, todo_model)
#     finally:
#         db.close()
