from django import forms
from .models import MissingPerson, MissingPersonContact, MissingPersonPhoto


class BasicInfoForm(forms.ModelForm):
    class Meta:
        model = MissingPerson
        fields = [
            "name",
            "gender",
            "age",
            "last_seen_location",
            "description",
            "county",
            "sub_county",
            "ward",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full name of the missing person",
                }
            ),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "age": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 120}
            ),
            "last_seen_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Where was the person last seen?",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Please provide detailed description including physical appearance, clothing last seen wearing, circumstances of disappearance, etc.",
                }
            ),
            "county": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "County"}
            ),
            "sub_county": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Sub County"}
            ),
            "ward": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ward"}
            ),
        }

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is not None and (age < 0 or age > 120):
            raise forms.ValidationError("Please enter a valid age between 0 and 120.")
        return age


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = MissingPersonContact
        fields = ["name", "phone_number", "email"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Contact person name"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+254 700 000 000"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "email@example.com"}
            ),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if phone:
            # Basic phone number validation
            import re

            # Remove spaces and common separators
            phone_clean = re.sub(r"[\s\-\(\)]", "", phone)
            if not re.match(r"^\+?[0-9]{10,15}$", phone_clean):
                raise forms.ValidationError("Please enter a valid phone number.")
        return phone


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = MissingPersonPhoto
        fields = ["photo", "description", "alternative_text"]
        widgets = {
            "photo": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*", "multiple": True}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Brief description of the photo",
                }
            ),
            "alternative_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Alternative text for accessibility",
                }
            ),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            # Validate file size (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file too large. Please keep it under 5MB."
                )

            # Validate file type
            if not photo.content_type.startswith("image/"):
                raise forms.ValidationError("Please upload a valid image file.")

        return photo
