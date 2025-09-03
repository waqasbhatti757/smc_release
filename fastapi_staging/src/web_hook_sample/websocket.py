from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
# from app.tasks import fetch_records
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="templates")
ws_connections = {}


@app.get("/")
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/{task_id}")
async def ws_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    ws_connections[task_id] = websocket
    try:
        while True:
            await websocket.receive_text()  # receive ping if needed
    except WebSocketDisconnect:
        ws_connections.pop(task_id, None)


@app.post("/trigger-task/")
def trigger_task():
    task_id = str(uuid.uuid4())
    # fetch_records.delay(task_id)
    return {"task_id": task_id}


@app.post("/task-callback/")
async def task_callback(request: Request):
    data = await request.json()
    task_id = data["task_id"]
    result = data["result"]

    websocket = ws_connections.get(task_id)
    if websocket:
        await websocket.send_json({"status": "done", "data": result})
    return JSONResponse({"ok": True})
