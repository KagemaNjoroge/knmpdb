from django.urls import path
from .views import dashboard, edit_missing_persons_report


app_name = "console"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("edit-report/<slug:slug>/", edit_missing_persons_report, name="edit_report"),
]
