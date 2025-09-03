from django.urls import path
from .views.campaign_crud import campaign_view as views
app_name = 'campaign_data'
urlpatterns = [
    path("add-campaign/", views.add_campaign_data, name="add_campaign_data"),
    path("delete-campaign/", views.delete_data, name="delete_data"),
    path("edit-campaign/", views.edit_campaign_data, name="edit_campaign_data"),
    path("read-campaign/", views.read_campaign_data, name="read_campaign_data"),
    path("report-pmc/", views.report_new_pmc, name="report_new_pmc"),
    path("reports-smc/", views.reports_smc, name="reports_smc"),
    path("smc-followup/", views.smc_follow_up, name="smc_follow_up"),
    path("manage_big_team_level_data/", views.manage_big_team_level_data, name="manage_big_team_level_data"),
    path("manage_big_child_level_data/", views.manage_big_child_level_data, name="manage_big_child_level_data"),
]




