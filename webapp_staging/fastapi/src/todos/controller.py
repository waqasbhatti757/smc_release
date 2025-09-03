# from fastapi import APIRouter, status
# from typing import List
# from uuid import UUID
# from fastapi.responses import JSONResponse
# from src..database.core import DbSession
# from src.auth import  models
# from src.auth import service
# from src..auth.service import CurrentUser
# from src.auth import celery_tasks
# import time
# import logging
#
# router = APIRouter(
#     prefix="/todos",
#     tags=["Todos"]
# )
#
#
# @router.post("/", response_model=models.TodoResponse, status_code=status.HTTP_201_CREATED)
# def create_todo(db: DbSession, todo: models.TodoCreate, current_user: CurrentUser):
#     # return service.create_todo(current_user, db, todo)
#
#     start_time = time.perf_counter()
#
#     result = service.create_todo(current_user, db, todo)
#
#     elapsed_time = time.perf_counter() - start_time
#     # logging.info(f"Todo created in {elapsed_time:.4f} seconds")
#     print(f"Todo created in {elapsed_time:.4f} seconds")
#     return result
#
# # @router.post("/", status_code=status.HTTP_202_ACCEPTED)
# # async def create_todo(db: DbSession, todo: models.TodoCreate, current_user: CurrentUser):
# #     # Serialize todo data
# #     todo_data = todo.model_dump()
# #     if hasattr(todo_data.get("priority"), "value"):
# #         todo_data["priority"] = todo_data["priority"].value
# #         celery_tasks.create_todo_task.delay(todo_data, current_user.user_id)
# #
# #     return JSONResponse(
# #         status_code=202,
# #         content={
# #             "message": "Todo creation scheduled in background",
# #             # "task_id": task.id,
# #             "status": "PENDING"
# #         }
# #     )
