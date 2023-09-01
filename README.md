# Atrice
Revamping attendance &amp; security: My project modernizes tracking with Python, Django &amp; facial recognition. User-friendly interface simplifies management &amp; enhances safety in education. Prioritizing data security, scalability, &amp; comprehensive campus management.
[![Watch the video](https://i.stack.imgur.com/Vp2cE.png)](https://youtu.be/vt5fpE0bzSY)


Atrice is a Django-based application that performs real-time face recognition on camera feeds and marks the attendance of recognized individuals. It uses the face_recognition library for face detection and recognition.

## Features

- Real-time face detection and recognition from camera feeds.
- Marking attendance for recognized individuals by associating them with registered students.
- Tracking Inside Campus: Updates the camera ID where the student was last spotted to track their movement within the campus premises.
- Data Augmentation and Preprocessing: During enrollment, the app performs histogram equalization and image augmentation to enhance the quality and variety of stored student images. Three images are stored for each person to improve recognition accuracy.
- User-friendly web interface for interacting with the application.
- Supports multiple cameras.

## Setup and Usage

1. Install the required libraries using `pip install face_recognition, opencv-python, celery`.
2. Ensure you have registered student images saved in the 'media/images' directory.
3. Configure the database settings in `settings.py`.
4. Run migrations using `python manage.py migrate` to create the necessary database tables.
5. Start the Django development server using `python manage.py runserver`.
6. Access the web app at http://localhost:8000/.
7. Register students and configure camera settings via the web interface.
8. Start the attendance marking process by navigating to the appropriate section of the web app.
9. The cameras can be activated and deactivated from the manage page.

## Directory Structure
```
Atrice/
├── manage.py
├── autolog/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pages/
│   ├── migrations/
│   │   ├── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── task.py <!-- install celery to schedule tasks to reset the attendance after a certain interval of time-->
│   ├── models.py
│   ├── models.py
│   ├── views.py
├── media/
│   ├── images/
│   │   ├── student.firstname_student.secondname_registernum.jpg
│   │   └── ... <!-- enrolled student's image will appear here -->
├── static/
│   ├── css/
│   │   └──  manage.css
│   ├── js/
│   │   └── manage.js
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── track.html
    ├── latecomers.html
    ├── enroll.html
    └── manage.html
```




## Note

- Ensure you have registered student images in the 'media/images' directory before running the application.
- Adjust the threshold and other parameters in the `process_frame` function for optimal performance.
- Face recognition accuracy may vary based on lighting conditions and image quality.

## Credits

This web app was developed by Shahil Malik for the Final year Mini project. It utilizes the [face_recognition](https://github.com/ageitgey/face_recognition) and [opencv-python](https://github.com/opencv/opencv-python) libraries, along with the Django framework.
