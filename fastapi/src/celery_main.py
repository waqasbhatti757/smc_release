# from celery import Celery
# # import eventlet
# # eventlet.monkey_patch()
#
# celery_app = Celery(
#     'app',
#     broker='redis://localhost:6379/0',
#     backend='redis:d//localhost:6379/1',
# )
#
# celery_app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     timezone='UTC',
#     enable_utc=True,
# )
#
# # ✅ Auto-discover tasks in these packages
# celery_app.autodiscover_tasks([
#     "src.todos.celery_tasks",
#     "src.users",
#     "src.auth",
# ])