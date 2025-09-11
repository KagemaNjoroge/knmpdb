from django.urls import path

from .views import (
    web_index,
    report_missing,
    all_missing_persons,
    about,
    missing_person_detail,
    favicon_ico,
    privacy_policy,
    terms_of_service,
)


app_name = "core"

urlpatterns = [
    path("", web_index, name="web_index"),
    path("favicon.ico", favicon_ico),
    path("report-missing-person/", report_missing, name="report_missing"),
    path("missing-persons/", all_missing_persons, name="all_missing_persons"),
    path(
        "missing-person/<slug:slug>/",
        missing_person_detail,
        name="missing_person_detail",
    ),
    path("about/", about, name="about"),
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
    path("terms-of-service/", terms_of_service, name="terms_of_service"),
]
