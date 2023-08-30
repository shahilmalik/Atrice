# tasks.py
# from celery import shared_task
from django.utils import timezone
from .models import UploadImage

# @shared_task
def reset_timestamps():
    UploadImage.objects.all().update(timestamp=None)
