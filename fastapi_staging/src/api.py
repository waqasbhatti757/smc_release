from fastapi import FastAPI
# from src.todos.controller import router as todos_router
from src.auth.controller import router as auth_router
from src.users.controller import router as users_router
from src.campaign.controller import router as campaign_router


def register_routes(app: FastAPI):

   app.include_router(auth_router)
   app.include_router(users_router)
   app.include_router(campaign_router)
