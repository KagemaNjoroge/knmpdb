from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from .models import MissingPerson, MissingPersonContact, MissingPersonPhoto
from django.db.models import Q
import os
from django.conf import settings
from django.contrib import messages
from django.core.files import File

import uuid


def cleanup_temp_files(photo_data):
    """Clean up temporary uploaded files"""
    for photo_info in photo_data:
        temp_path = photo_info.get("temp_path")
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass  # File already deleted or permission error


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
@login_required  # probably should be removed later to allow public reporting
def report_missing(request):
    current_step = request.session.get("report_step", 1)
    form_data = request.session.get("form_data", {})

    if request.method == "POST":
        # Handle going back to previous step
        if request.POST.get("action") == "previous_step":
            # Clean up temporary files if going back from step 3 to 2
            if current_step == 3 and "photos" in form_data:
                cleanup_temp_files(form_data["photos"])
                del form_data["photos"]
                request.session["form_data"] = form_data

            current_step = max(1, current_step - 1)
            request.session["report_step"] = current_step
            return redirect("core:report_missing")

        step = int(request.POST.get("step", current_step))

        if step == 1:
            # Process basic info form
            form_data.update(
                {
                    "name": request.POST.get("name", ""),
                    "age": request.POST.get("age", ""),
                    "gender": request.POST.get("gender", ""),
                    "last_seen_location": request.POST.get("last_seen_location", ""),
                    "county": request.POST.get("county", ""),
                    "sub_county": request.POST.get("sub_county", ""),
                    "ward": request.POST.get("ward", ""),
                    "description": request.POST.get("description", ""),
                }
            )
            current_step = 2

        elif step == 2:
            # Process photos form

            photos = request.FILES.getlist("photos")
            photo_data = []

            for i, photo in enumerate(photos):
                # Validate photo
                if photo.size > 5 * 1024 * 1024:  # 5MB limit

                    messages.error(
                        request,
                        f"Photo {photo.name} is too large. Please keep photos under 5MB.",
                    )
                    continue

                if not photo.content_type.startswith("image/"):

                    messages.error(request, f"File {photo.name} is not a valid image.")
                    continue

                # Save photo temporarily
                temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_uploads")
                os.makedirs(temp_dir, exist_ok=True)

                file_extension = os.path.splitext(photo.name)[1]
                temp_filename = f"temp_{uuid.uuid4()}{file_extension}"
                temp_path = os.path.join(temp_dir, temp_filename)

                # Save the file temporarily
                with open(temp_path, "wb+") as destination:
                    for chunk in photo.chunks():
                        destination.write(chunk)

                photo_info = {
                    "temp_path": temp_path,
                    "original_name": photo.name,
                    "content_type": photo.content_type,
                    "size": photo.size,
                    "description": request.POST.get(f"photo_description_{i}", ""),
                    "alt_text": request.POST.get(f"photo_alt_text_{i}", ""),
                }
                photo_data.append(photo_info)

            form_data["photos"] = photo_data
            current_step = 3

        elif step == 3:
            # Process contacts form and create the missing person record
            contacts_data = []

            # Get all contact fields
            contact_fields = [
                key for key in request.POST.keys() if key.startswith("contact_name_")
            ]

            for field in contact_fields:
                contact_num = field.split("_")[-1]
                contact_name = request.POST.get(f"contact_name_{contact_num}", "")
                phone_number = request.POST.get(f"phone_number_{contact_num}", "")
                email = request.POST.get(f"email_{contact_num}", "")

                if contact_name and phone_number:  # At least name and phone required
                    contacts_data.append(
                        {
                            "name": contact_name,
                            "phone_number": phone_number,
                            "email": email,
                        }
                    )

            # Create the missing person record
            try:

                # Validate required fields
                if (
                    not form_data.get("name")
                    or not form_data.get("gender")
                    or not form_data.get("last_seen_location")
                    or not form_data.get("description")
                ):
                    messages.error(request, "Please fill in all required fields.")
                    current_step = 1
                    request.session["report_step"] = current_step
                    return redirect("core:report_missing")

                if not contacts_data:
                    messages.error(request, "At least one contact is required.")
                    current_step = 3
                    request.session["report_step"] = current_step
                    return redirect("core:report_missing")

                # Create missing person
                missing_person = MissingPerson.objects.create(
                    name=form_data.get("name"),
                    gender=form_data.get("gender"),
                    age=int(form_data.get("age")) if form_data.get("age") else None,
                    last_seen_location=form_data.get("last_seen_location"),
                    county=form_data.get("county", ""),
                    sub_county=form_data.get("sub_county", ""),
                    ward=form_data.get("ward", ""),
                    description=form_data.get("description"),
                    status="missing",
                )

                # Create contacts
                for contact_data in contacts_data:
                    contact = MissingPersonContact.objects.create(**contact_data)
                    missing_person.contacts.add(contact)

                # Create photos
                if "photos" in form_data:

                    for i, photo_info in enumerate(form_data["photos"]):
                        # Read the temporary file and create a Django File object
                        temp_path = photo_info["temp_path"]

                        if os.path.exists(temp_path):
                            with open(temp_path, "rb") as temp_file:
                                django_file = File(temp_file)
                                django_file.name = photo_info["original_name"]

                                photo = MissingPersonPhoto.objects.create(
                                    description=photo_info["description"],
                                    alternative_text=photo_info["alt_text"],
                                    is_primary=(i == 0),  # First photo is primary
                                )

                                # Save the file to the photo field
                                photo.photo.save(
                                    photo_info["original_name"], django_file, save=True
                                )

                                missing_person.photos.add(photo)

                            # Clean up temporary file
                            try:
                                os.remove(temp_path)
                            except OSError:
                                pass  # File already deleted or doesn't exist

                # Clear session data
                request.session.pop("report_step", None)
                request.session.pop("form_data", None)

                # Add success message
                messages.success(
                    request, "Missing person report submitted successfully!"
                )

                # reset to step 1 for new report
                request.session["report_step"] = 1
                request.session["form_data"] = {}
                # Redirect to success page
                return redirect("core:report_missing")

            except Exception as e:
                # Handle errors and cleanup temp files

                if "photos" in form_data:
                    cleanup_temp_files(form_data["photos"])

                messages.error(request, f"Error creating report: {str(e)}")
                current_step = 3

        # Update session
        request.session["report_step"] = current_step
        request.session["form_data"] = form_data

        return redirect("core:report_missing")

    return render(
        request,
        "core/report.html",
        {"current_step": current_step, "form_data": form_data},
    )


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
    missing_person = get_object_or_404(
        MissingPerson.objects.prefetch_related("photos", "contacts"), slug=slug
    )

    return render(
        request, "core/missing_person_detail.html", {"missing_person": missing_person}
    )


def about(request: HttpRequest):
    return render(request, "core/about.html")


def privacy_policy(request: HttpRequest):
    return render(request, "core/privacy_policy.html")


def terms_of_service(request: HttpRequest):
    return render(request, "core/terms_of_service.html")
