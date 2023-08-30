from modulefinder import IMPORT_NAME
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import ImageUploadForm
from django.http import JsonResponse
from .models import UploadedImage, ClassRoom
from django.shortcuts import render
from django.http import JsonResponse
from .models import UploadedImage
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from tkinter import E
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime,time
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def process_frame(img, encodeListKnown, attendance_data, camid, classNames,threshold=0.5):
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = histogram_equalization(imgS)
    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        minDistance = min(faceDis)
        if minDistance <= threshold:
            closestMatchIndex = np.argmin(faceDis)
            name = classNames[closestMatchIndex].upper()
            #print(name)

            if name not in attendance_data:
                attendance_entry = markAttendance(name,camid)
                if attendance_entry:
                    attendance_data.append(name)

def markAttendance(name, camid):
    reg = name.split('_')[-1]
    students = UploadedImage.objects.filter(register_number=reg)
    
    if students.exists():
        student = students.first()
        print(f"{student.name} spotted at {camid}")
        student.lastspotted = camid

        if student.timestamp is None:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            student.timestamp = dtString
            print(f"Attendance Marked for {student.name} at {dtString}")
        
        student.save()
                
def findEncodings(images):
        encodeList=[]
        for img in images:
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList


    
        

def histogram_equalization(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized_image = cv2.equalizeHist(gray_image)
    equalized_color_image = cv2.cvtColor(equalized_image, cv2.COLOR_GRAY2BGR)
    return equalized_color_image

@require_POST
@csrf_exempt
def demo_view(request):
    global stop_thread
    stop_thread = False
    num_cameras = int(request.POST.get("num_cameras", 1))  # Get the num_cameras value
    available_cameras = []
    cap_list=[]
    for i in range(4):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap_list.append(cap)
        else:
            print(f"Camera {i} is not available.")

    if num_cameras > len(available_cameras):
        for cap in cap_list:
            cap.release()
        error_message = f"Error: The specified number of cameras is {num_cameras}, but only {len(available_cameras)} available on this device"
        print(error_message)  
        return HttpResponse(error_message) 


    images = []
    path = 'media/images'
    classNames = []
    myList = os.listdir(path)
    for cls in myList:
        curImg = cv2.imread(f'{path}/{cls}')
        images.append(curImg)
        classNames.append(os.path.splitext(cls)[0])

    print("Encoding the faces ...")
    
    encodeListKnown = findEncodings(images)


    cap_list = []
    cap_dict = {}
    if num_cameras >= 1:
        cap_dict[1] = {"cap": cv2.VideoCapture(0), "ret": False, "img": None}
    if num_cameras >= 2:
        cap_dict[2] = {"cap": cv2.VideoCapture(1), "ret": False, "img": None}
    if num_cameras >= 3:
        cap_dict[3] = {"cap": cv2.VideoCapture(2), "ret": False, "img": None}
    if num_cameras >= 4:
        cap_dict[4] = {"cap": cv2.VideoCapture(3), "ret": False, "img": None}

    while not stop_thread:
        attendance_data = []
        for cap_data in cap_dict.values():
            cap = cap_data["cap"]
            ret, img = cap.read()
            cap_data["ret"] = ret
            cap_data["img"] = img

        for cap_id, cap_data in cap_dict.items():
            ret, img = cap_data["ret"], cap_data["img"]
            if ret:
                process_frame(img, encodeListKnown, attendance_data, f"CAM{cap_id}", classNames)

        if len(attendance_data) > 0:
            print(*attendance_data, sep='\n')

    for cap_data in cap_dict.values():
        cap = cap_data["cap"]
        cap.release()

    return render(request, 'latecomers.html')

@require_POST
@csrf_exempt
def stop_demo_loop(request):
    global stop_thread
    stop_thread = True
    print("stop_demo_loop executed")
    return HttpResponse("Camera loop stopping...")

def track_view(request):
    students=UploadedImage.objects.all()
    students_data = []
    for student in students:
        student_data = {
            'register_number': student.register_number,
            'name': student.name,
            'year': student.year,
            'specialization': student.specialization,
            'section': student.section,
            'timestamp': student.timestamp.strftime("%I:%M %p") if student.timestamp else "ABSENT", 
            'lastspotted': student.lastspotted,
        }
          

        students_data.append(student_data)

    students_json = json.dumps(students_data)

    context = {
        'students_json': students_json,
    }
    return render(request,"track.html",context)
                        

def latecomers(request):
    late_time="08:10 AM"
    students=UploadedImage.objects.all()
    students_data = []
    print(late_time)
    for student in students:
        student_data = {
            'register_number': student.register_number,
            'name': student.name,
            'year': student.year,
            'specialization': student.specialization,
            'section': student.section,
            'timestamp': student.timestamp.strftime("%I:%M %p") if student.timestamp else "ABSENT", 
        }
          

        students_data.append(student_data)

    students_json = json.dumps(students_data)

    result = {
        'students_json': students_json,
    }
    return render(request,"latecomers.html",result)



def manage(request):
    students = UploadedImage.objects.all()

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES, auto_id='file_%s')
        if form.is_valid():
            uploaded_images = []

            for i, image_file in enumerate(request.FILES.getlist('image')):
                filename_parts = image_file.name.split('/')
                if len(filename_parts) != 5:
                    form.errors['image_{}'.format(i)] = ['Invalid filename format']
                else:
                    uploaded_images.append(image_file)

            # Save the valid images
            for image_file in uploaded_images:
                new_form = ImageUploadForm({'image': image_file})
                uploaded_image = new_form.save(commit=False)
                uploaded_image.save()

            return redirect('demo')
    else:
        form = ImageUploadForm(auto_id='file_%s')  # Initialize form when not in POST request

    students_data = []
    for student in students:
        student_data = {
            'register_number': student.register_number,
            'name': student.name,
            'year': student.year,
            'specialization': student.specialization,
            'section': student.section,
            'image_url': student.image.url,
        }
        students_data.append(student_data)

    students_json = json.dumps(students_data)

    context = {
        'students_json': students_json,
        'form': form,  
    }
    return render(request, 'manage.html', context)


def is_valid_image(image, max_size_mb=6):

    image_size_mb = image.size / (1024 * 1024)  
    if image_size_mb > max_size_mb:
        return False
    img = face_recognition.load_image_file(image)
    face_locations = face_recognition.face_locations(img)

    if len(face_locations) == 0:
        return False
    return True

def enroll(request):
    error_message = None
    success_message = None

    if request.method == 'POST':
        register_number = request.POST.get('registerNumber').upper()
        name = request.POST.get('name').upper()
        year = request.POST.get('year')
        specialization = request.POST.get('specialization')
        section = request.POST.get('section')
        image = request.FILES.get('image')

        existing_entry = UploadedImage.objects.filter(register_number=register_number).first()
        if existing_entry:
            error_message = f"{register_number} already exists"
        elif not is_valid_image(image):
            error_message = f"img should contain a face and be < 6MB"
        else:
            try:
                uploaded_image = UploadedImage(
                    register_number=register_number,
                    name=name,
                    year=year,
                    specialization=specialization,
                    section=section,
                    image=image
                )
                uploaded_image.save()
                success_message = f"{name}'s Data saved successfully"
                newimgname = "_".join(name.split(" ")[:2])
                image = cv2.imread(f"media/images/{newimgname}_{register_number}.jpg")
                output_directory = "media/images"
                augmented_image = augment_image(image)
                equalized_image1 = histogram_equalization(image)

                output_filename = os.path.join(output_directory, f"{newimgname}2_{register_number}.jpg")
                output_filename2 = os.path.join(output_directory, f"{newimgname}3_{register_number}.jpg")
                equalized_image2 = histogram_equalization(augmented_image)
                cv2.imwrite(output_filename2,equalized_image1)
                cv2.imwrite(output_filename,equalized_image2)
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
    context = {
        'error_message': error_message,
        'success_message': success_message
    }

    return render(request, 'enroll.html', context)

def augment_image(image):
    angle = np.random.randint(-10, 10)  # Adjust the angle range as needed
    rows, cols, _ = image.shape
    rotation_matrix = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))

    # Apply horizontal flip with a certain probability
    if np.random.rand() > 0.5:
        rotated_image = cv2.flip(rotated_image, 1)

    # Apply brightness and contrast adjustment
    brightness = np.random.uniform(0.8, 1.2)  # Adjust the brightness range as needed
    contrast = np.random.uniform(0.8, 1.2)    # Adjust the contrast range as needed
    adjusted_image = cv2.convertScaleAbs(rotated_image, alpha=contrast, beta=brightness)

    return adjusted_image

def histogram_equalization(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized_image = cv2.equalizeHist(gray_image)
    equalized_color_image = cv2.cvtColor(equalized_image, cv2.COLOR_GRAY2BGR)
    return equalized_color_image


def delete_student(request, register_number):
    if request.method == 'DELETE':
        student = get_object_or_404(UploadedImage, register_number=register_number)
        student.image.delete()
        media_path = os.path.join('media', 'images')
        for filename in os.listdir(media_path):
            if filename.endswith(f'{register_number}.jpg'):
                file_path = os.path.join(media_path, filename)
                os.remove(file_path)
        student.delete()
        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'message': 'Invalid method'})

def resetatt(request):
    #UploadedImage.objects.all().update(timestamp=None)
    # ClassRoom.objects.all().update(presents=0,absents=0,latecomers=0,strength=0)
    # UploadedImage.objects.all().delete()
    # classe =ClassRoom.objects.all()
    # for cl in classe:
    #     year = ['I', 'II', 'III', 'IV']
    #     specialization = ['CSE', 'AIML', 'BDA', 'CSBS']
    #     section = ['A', 'B', 'C', 'D']

    #     combinations = []

    #     for y in year:
    #         for s in specialization:
    #             for sec in section:
    #                 combination = f'{y}-{s}-{sec}'
    #                 combinations.append(combination)

    #     for combo in combinations:
    #         year, specialization, section = combo.split('-')
    #         if(cl.name==f'Class {year} {specialization} {section}'):
    #             cl.name=combo
    #             cl.save()
    return render(request,"latecomers.html")



def dashboard_view(request):
    classroom_data = []
    classrooms = ClassRoom.objects.all()
    students = UploadedImage.objects.all()
    fstrength=0
    fabsent=0
    flatecomers=0
    for cl in classrooms:
        cl.strength=0
        cl.absents=0
        cl.latecomers=0
        year,spec,sec = cl.name.split('-')
        for student in students:
            if(student.year ==year and student.specialization==spec and student.section==sec):
                if(cl.name==f'{year}-{spec}-{sec}'):
                    cl.strength+=1
                    fstrength+=1
                    if not student.timestamp:
                        cl.absents+=1
                        fabsent+=1
                    else:
                        if student.timestamp>time(8,10,0):
                            cl.latecomers+=1
                            flatecomers+=1
        cl.presents=cl.strength-cl.absents
        fpresent=fstrength-fabsent
        ontime=cl.presents-cl.latecomers
        fontime=fpresent-flatecomers
        classroom_d = {
            'name': cl.name,
            'latecomers': cl.latecomers,
            'absents': cl.absents,
            'presents': cl.presents,
            'strength':cl.strength,
            'ontime': ontime,
        }
        if (cl.strength>0):
            classroom_data.append(classroom_d)

    # Encode classroom_data as JSON
    fdata={
        'name': "All-Classes",
        'latecomers': flatecomers,
        'absents': fabsent,
        'presents': fpresent,
        'strength':fstrength,
        'ontime': fontime,
    }
    classroom_data.insert(0, fdata)
    classroom_data_json = json.dumps(classroom_data)
    print(classroom_data_json)
    
    return render(request, 'dashboard.html', {"classroom_data_json": classroom_data_json})
