from django.contrib import admin

from .models import UploadedImage,ClassRoom

# Register your models here.
admin.site.register(UploadedImage)
admin.site.register(ClassRoom)