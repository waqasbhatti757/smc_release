from django.urls import path
from .views.auth_process.authenticate_view import login_view,logout

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout, name='logout'),
]
