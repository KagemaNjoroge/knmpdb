from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods

from .models import MissingPerson


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
    # TODO: implement search and filters
    # all missing persons status="missing" order by created_at desc
    all_missing_persons = MissingPerson.objects.filter(status="missing").order_by(
        "-created_at"
    )
    paginator = Paginator(all_missing_persons, 10)  # 10 persons per page
    missing_persons = paginator.get_page(page)
    return render(
        request, "core/missing_persons.html", {"missing_persons": missing_persons}
    )


def missing_person_detail(request, slug):
    missing_person = get_object_or_404(MissingPerson, slug=slug)

    return render(
        request, "core/missing_person_detail.html", {"missing_person": missing_person}
    )


def about(request):
    return render(request, "core/about.html")
