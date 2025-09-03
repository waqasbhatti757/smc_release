from django.urls import path
# from .views.auth_process.authenticate_view import login_view,dashboard,logout
from .views.dashboard_view.dashview import dashboard_view


app_name = 'dashboard'

urlpatterns = [
    path('user_dashboard/', dashboard_view, name='user_dashboard'),
]
