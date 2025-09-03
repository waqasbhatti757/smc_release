from fastapi import FastAPI
from .database.core import engine, Base
from .entities.todo import Todo  # Import models to register them
from .entities.user import User  # Import models to register them
from .api import register_routes
from .logging import configure_logging, LogLevels
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