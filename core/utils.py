import phonenumbers
import os
from uuid import uuid4


def generate_unique_filename(instance, filename):
    """
    Generate a unique filename using UUID while preserving the original file extension
    """
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{ext}"
    return os.path.join(instance.get_upload_path(), filename)


def format_phone_number(phone_number):
    """
    Format the phone number to international format.
    """
    try:
        phone_number = phonenumbers.parse(phone_number, "KE")
        return phonenumbers.format_number(
            phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
    except phonenumbers.NumberParseException:
        raise ValueError("Invalid phone number format")
