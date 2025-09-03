from django.urls import path
from .views.campaign_view.plan_view import sync_planning,campaign_planning

app_name = 'campaign_planning'
urlpatterns = [
    path('planning/', sync_planning, name='planning'),
    path('campaign_planning/', campaign_planning, name='campaign_planning'),
]

