from django.urls import path
from .views.userview.user_view import create_user,manage_user,update_settings,update_user_profile,get_users_api,edit_user_profile,full_profile_update
from .views.userview.user_view import get_user_info_for_js
app_name = 'usermanagement'
urlpatterns = [
    path('create_user/', create_user, name='create_user'),
    path('update_user_profile/', update_user_profile, name='update_user_profile'),
    path('manage_user/', manage_user, name='manage_user'),
    path('update_settings/', update_settings, name='update_settings'),
    path('/api/users', get_users_api, name='get_users_api'),
    path('edit_profile/', edit_user_profile, name='edit_user_profile'),
    path('full_profile_update/', full_profile_update, name='full_profile_update'),
    path('get_user_info_for_js/', get_user_info_for_js, name='get_user_info_for_js'),

]
