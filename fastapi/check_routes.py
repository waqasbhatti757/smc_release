# /opt/smc_fastapi/check_routes.py

from src.main import app

print([route.path for route in app.routes])

