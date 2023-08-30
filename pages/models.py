from tkinter.tix import Tree
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from .validators import validate_image_filename
from datetime import time

from django.db import models

class UploadedImage(models.Model):
    register_number = models.CharField(max_length=15,unique=True)
    name = models.CharField(max_length=100)
    
    YEAR_CHOICES = [
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
        ('IV', 'IV')
    ]
    year = models.CharField(max_length=3, choices=YEAR_CHOICES)
    
    SPECIALIZATION_CHOICES = [
        ('CSE', 'CSE'),
        ('AIML', 'AIML'),
        ('BDA', 'BDA'),
        ('CSBS', 'CSBS')
    ]
    specialization = models.CharField(max_length=4, choices=SPECIALIZATION_CHOICES)
    
    SECTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)

    def image_upload_path(instance,filename):
        first_two_names = instance.name.split()[:2]
        first_two_names_lower = '_'.join(first_two_names).lower()
        new_filename = f"{first_two_names_lower}_{instance.register_number}.jpg"
        return f'images/{new_filename}'
    
    image = models.ImageField(upload_to=image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.TimeField(default=None, blank=True, null=True)
    lastspotted=models.CharField(max_length=10, default=None, null=True, blank=True)


    @classmethod
    def createStudent(cls):
        instances=[]
        yr = ['I', 'II', 'III', 'IV']
        spec = ['CSE', 'AIML', 'BDA', 'CSBS']
        sec = ['A', 'B', 'C', 'D']

        for i in range(1, 50):
            yrv = yr[(i // 5) % 4]
            spv = spec[(i // 3) % 4]
            sev = sec[(i // 2) % 4]
            if(sev=="B"):
                ts=time(8,7,0)
            else:
                ts = time(10, 18, 0)
                if(i%11):
                    ts = time(8, 0, 0)
                
                if (i % 6==0):
                    ts = None
            instance=cls(register_number = f"{spv}{i}",name=f"STUDENT {i}",year=yrv,specialization=spv,section=sev,timestamp=ts,image="media/images/shahil.jpg")
            instances.append(instance)
        cls.objects.bulk_create(instances)


# class UploadedImage(models.Model):
#     image = models.ImageField(upload_to='uploads/', validators=[validate_image_filename])
#     uploaded_at = models.DateTimeField(auto_now_add=True)


class ClassRoom(models.Model):
    name = models.CharField(max_length=30, unique=True)
    strength = models.IntegerField(blank=True, null=True, default=None)
    latecomers = models.IntegerField(blank=True, null=True, default=None)
    absents = models.IntegerField(blank=True, null=True, default=None)
    presents = models.IntegerField(blank=True, null=True, default=None)
    
    @classmethod
    def nameClass(cls):
        year = ['I', 'II', 'III', 'IV']
        specialization = ['CSE', 'AIML', 'BDA', 'CSBS']
        section = ['A', 'B', 'C', 'D']

        combinations = []

        for y in year:
            for s in specialization:
                for sec in section:
                    combination = f'{y}-{s}-{sec}'
                    combinations.append(combination)

        instances = []
        for combo in combinations:
            year, specialization, section = combo.split('-')
            instance = cls(name=f'Class {year} {specialization} {section}')
            instances.append(instance)

        cls.objects.bulk_create(instances)

# Call the class method to create instances
# ClassRoom.nameClass()
# t=1
# while(t!=0):
#     UploadedImage.createStudent()
#     t=0
