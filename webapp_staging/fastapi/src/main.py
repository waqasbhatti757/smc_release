from fastapi import FastAPI
from src.database.core import engine, Base
from src.entities.todo import Todo  # Import models to register them
from src.entities.user import User  # Import models to register them
from src.api import register_routes
from src.custom_logging import configure_logging, LogLevels
from fastapi.middleware.cors import CORSMiddleware


configure_logging(LogLevels.info)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://192.168.2.232:8000", "http://192.168.1.105:8000"],  # front-end origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" Only uncomment below to create new tables, 
otherwise the pytest will fail if not connected
"""
# Base.metadata.create_all(bind=engine)

register_routes(app)
