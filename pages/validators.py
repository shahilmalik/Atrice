from django.core.exceptions import ValidationError
import re

def validate_image_filename(value):
    pattern = re.compile(r'^[A-Z]{2}\d{10}\/[A-Z\s]+\s[A-Z\s]+\s[A-Z\s]+\s[A-Z\s]+\/[1-4]\/(CSE|AIML|BDA|CSBS)\/[A-Z]\/[A-Z\s]+\.jpg$')
    if not pattern.match(value):
        raise ValidationError(
            'Invalid image file name format. It should be "RegisterNumber/Name/Year/Specialization/Section.jpg".'
        )
