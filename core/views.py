from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest
from .models import MissingPerson
from django.db.models import Q


def favicon_ico(request):
    # TODO: serve actual favicon.ico file, add a better one
    favicon_path = "/static/images/hero-tech-face.svg"
    return redirect(favicon_path)


def web_index(request):
    # 3 latest missing persons
    latest_missing_persons = MissingPerson.objects.filter(status="missing").order_by(
        "-created_at"
    )[:3]
    return render(
        request, "core/index.html", {"latest_missing_persons": latest_missing_persons}
    )


@require_http_methods(["GET", "POST"])
def report_missing(request):
    if request.method == "POST":
        # process form data
        pass
    return render(request, "core/report.html")


def all_missing_persons(request):
    page = request.GET.get("page", 1)

    # search and filter parameters
    search_query = request.GET.get("q", "").strip()
    gender_filter = request.GET.get("gender", "")
    age_min = request.GET.get("age_min", "")
    age_max = request.GET.get("age_max", "")

    #  all missing persons
    all_missing_persons = MissingPerson.objects.filter(status="missing").order_by(
        "-created_at"
    )

    # Apply search filter
    if search_query:

        all_missing_persons = all_missing_persons.filter(
            Q(name__icontains=search_query)
            | Q(last_seen_location__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(county__icontains=search_query)
            | Q(sub_county__icontains=search_query)
            | Q(ward__icontains=search_query)
        )

    # gender filter
    if gender_filter:
        all_missing_persons = all_missing_persons.filter(gender=gender_filter)

    # age range filter
    if age_min:
        try:
            age_min_int = int(age_min)
            all_missing_persons = all_missing_persons.filter(age__gte=age_min_int)
        except ValueError:
            pass  # Invalid age_min, ignore

    if age_max:
        try:
            age_max_int = int(age_max)
            all_missing_persons = all_missing_persons.filter(age__lte=age_max_int)
        except ValueError:
            pass  # Invalid age_max, ignore

    # prefetch related data
    all_missing_persons = all_missing_persons.prefetch_related("photos", "contacts")

    paginator = Paginator(all_missing_persons, 12)  # 12 persons per page
    missing_persons = paginator.get_page(page)

    return render(
        request,
        "core/missing_persons.html",
        {
            "missing_persons": missing_persons,
            "current_page": page,
            "search_query": search_query,
            "gender_filter": gender_filter,
            "age_min": age_min,
            "age_max": age_max,
        },
    )


def missing_person_detail(request, slug):
    missing_person = get_object_or_404(MissingPerson, slug=slug)

    return render(
        request, "core/missing_person_detail.html", {"missing_person": missing_person}
    )


def about(request: HttpRequest):
    return render(request, "core/about.html")


def privacy_policy(request: HttpRequest):
    return render(request, "core/privacy_policy.html")


def terms_of_service(request: HttpRequest):
    return render(request, "core/terms_of_service.html")
