from django.contrib import admin
from .models import MissingPerson, MissingPersonPhoto, MissingPersonContact


# Inline: show photos inside MissingPerson admin
class MissingPersonPhotoInline(admin.TabularInline):
    model = MissingPerson.photos.through  # through table for ManyToMany
    extra = 1
    verbose_name = "Photo"
    verbose_name_plural = "Photos"


# Inline: show contacts inside MissingPerson admin
class MissingPersonContactInline(admin.TabularInline):
    model = MissingPerson.contacts.through
    extra = 1
    verbose_name = "Contact"
    verbose_name_plural = "Contacts"


@admin.register(MissingPerson)
class MissingPersonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gender",
        "age",
        "county",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "county",
        "gender",
        "created_at",
    )
    search_fields = ("name", "description", "last_seen_location")
    # prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)

    inlines = [MissingPersonPhotoInline, MissingPersonContactInline]


@admin.register(MissingPersonPhoto)
class MissingPersonPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "created_at")
    search_fields = ("description",)
    ordering = ("-created_at",)


@admin.register(MissingPersonContact)
class MissingPersonContactAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "email", "created_at")
    search_fields = ("name", "phone_number", "email")
    ordering = ("-created_at",)
