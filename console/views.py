from django.http import HttpRequest
from core.models import MissingPerson
from django.shortcuts import get_object_or_404, render
from django.db import models
from typing import Dict, Any, List
from django.contrib.admin.views.decorators import staff_member_required


def get_gender_stats(missing_persons) -> List[Dict[str, Any]]:

    most_missing_gender = (
        missing_persons.values("gender")
        .annotate(count=models.Count("gender"))
        .order_by("-count")
    )
    most_missing = most_missing_gender.first()
    other_missing_gender = most_missing_gender.last()

    gender_stats = [
        {
            "gender": most_missing["gender"],
            "count": most_missing["count"],
            "percentage": (
                round((most_missing["count"] / missing_persons.count()) * 100, 2)
                if missing_persons.count() > 0
                else 0
            ),
        },
        {
            "gender": other_missing_gender["gender"],
            "count": other_missing_gender["count"],
            "percentage": (
                round(
                    (other_missing_gender["count"] / missing_persons.count()) * 100, 2
                )
                if missing_persons.count() > 0
                else 0
            ),
        },
    ]

    return gender_stats


# only accessible by admin users
@staff_member_required
def dashboard(request: HttpRequest):
    # missing persons
    missing_persons = MissingPerson.objects.all().order_by("-created_at")
    # simple statistics
    still_missing = missing_persons.filter(status="missing").count()
    resolved_cases = missing_persons.exclude(status="missing").count()
    # county with most missing persons
    county_with_most_missing = (
        missing_persons.values("county")
        .annotate(count=models.Count("id"))
        .order_by("-count")
        .first()
    )
    # gender stats

    gender_stats = get_gender_stats(missing_persons)

    # median age of missing persons
    ages = list(missing_persons.exclude(age__isnull=True).values_list("age", flat=True))
    median_age = None
    if ages:
        ages.sort()
        n = len(ages)
        if n % 2 == 1:
            median_age = ages[n // 2]
        else:
            median_age = (ages[n // 2 - 1] + ages[n // 2]) / 2

    context = {
        "total_missing": missing_persons.count(),
        "still_missing": still_missing,
        "resolved_cases": resolved_cases,
        "county_with_most_missing": county_with_most_missing,
        "median_age": median_age,
        "page_items": missing_persons,  # Pass all items for DataTables to handle
        "gender_stats": gender_stats,
    }

    return render(request, "console/dashboard.html", context)


# only accessible by admin users
@staff_member_required
def edit_missing_persons_report(request: HttpRequest, slug: str):
    missing_person = get_object_or_404(MissingPerson, slug=slug)
    return render(
        request, "console/edit_report.html", {"missing_person": missing_person}
    )
