# from app.celery_app import celery_app
# import time
# import requests
#
# @celery_app.task
# def fetch_records(task_id):
#     # Simulate fetching 1M records
#     time.sleep(5)
#     data = [f"record_{i}" for i in range(10**6)]  # simulate large payload
#
#     # Send callback to FastAPI
#     requests.post("http://localhost:8000/task-callback/", json={
#         "task_id": task_id,
#         "result": f"Fetched {len(data)} records"
#     })
