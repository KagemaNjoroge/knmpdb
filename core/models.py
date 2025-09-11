from django.db import models
from django_extensions.db.models import AutoSlugField
from .utils import format_phone_number, generate_unique_filename


class Status(models.TextChoices):
    MISSING = "missing", "Missing"
    FOUND_PENDING = "found_pending", "Found - Pending Confirmation"
    FOUND_CONFIRMED = "found_confirmed", "Found - Confirmed"


class TimestampedModel(models.Model):
    """
    Abstract model for timestamp fields
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MissingPersonPhoto(TimestampedModel):

    photo = models.ImageField(upload_to=generate_unique_filename)
    description = models.TextField(blank=True)
    alternative_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Photo {self.id} - {self.description[:20]}"

    def get_upload_path(self):
        return "missing_person_photos/"


class MissingPersonContact(TimestampedModel):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.phone_number:
            try:
                self.phone_number = format_phone_number(self.phone_number)
            except ValueError:
                pass  # Invalid phone number, save as is
        super().save(*args, **kwargs)


class MissingPerson(TimestampedModel):

    genders = (("M", "Male"), ("F", "Female"))

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=genders)
    age = models.PositiveIntegerField(null=True, blank=True)
    last_seen_location = models.CharField(max_length=255)
    description = models.TextField()
    photos = models.ManyToManyField(MissingPersonPhoto, blank=True)

    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    ward = models.CharField(max_length=100, blank=True)

    # a missing person can have multiple contacts
    contacts = models.ManyToManyField(MissingPersonContact, blank=True)

    # extra fields
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.MISSING
    )
    date_found = models.DateTimeField(null=True, blank=True)

    # slug field for SEO-friendly URLs
    slug = AutoSlugField(
        populate_from="name", unique=True, max_length=255, db_index=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Save the object first to get an ID
        super().save(*args, **kwargs)

        # Then handle photo primary setting if photos exist
        if (
            self.pk
            and self.photos.exists()
            and not self.photos.filter(is_primary=True).exists()
        ):
            first_photo = self.photos.first()
            if first_photo:
                first_photo.is_primary = True
                first_photo.save()
