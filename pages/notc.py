from tkinter import E
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from deepface import DeepFace
import time

path='media/images'
images=[]
classNames =[]
myList = os.listdir(path)
print(myList)
for cls in myList:
    curImg= cv2.imread(f'{path}/{cls}')
    images.append(curImg)
    classNames.append(os.path.splitext(cls)[0])
print(classNames)

def findEncodings(images):
    encodeList=[]
    for img in images:
        imgc = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(imgc)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    with open('media/attendance.csv','r+') as f:
        myDataList=f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString= now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

print("Att marked")
encodeListKnown=findEncodings(images)  
print('encodeListKnown')


def process_frame(img, encodeListKnown, attendance_data, camid, threshold=0.6, verification_threshold=0.3, verification_image_size=(160, 160)):
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndices = [i for i, distance in enumerate(faceDis) if distance <= threshold]


        if any(matchIndices):
            for i in matchIndices:
                name = classNames[i].upper()
                try:
                    # Resize the verification images to the specified size
                    verification_img_resized = cv2.resize(images[i], verification_image_size)
                    verification_result = DeepFace.verify(img, verification_img_resized, model_name="Facenet", distance_metric="cosine", enforce_detection=False)
                    if verification_result['verified'] and verification_result['distance'] <= verification_threshold:
                        print(f"Verified: {name} & {camid}")
                        attendance_entry = markAttendance(name)
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        if attendance_entry:
                            attendance_data.append(attendance_entry)
                except ValueError as e:
                    print(f"Verification failed for {name}: {e}")





cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

# frame_skip = 3  # Process every 3rd frame
# frame_count = 0

while True:
    attendance_data = []

    # Read frames from the camera
    ret1, img1 = cap1.read()
    ret2, img2 = cap2.read()

    # Process frames only if ret is True (frame was read successfully)
    if ret1 and ret2:
        # frame_count += 1
        # if frame_count % frame_skip == 0:  # Process every Nth frame
        process_frame(img1, encodeListKnown, attendance_data,"maccam")
        process_frame(img2, encodeListKnown, attendance_data,"maccam")

        if len(attendance_data) > 0:
            print(*attendance_data, sep='\n')

        # Display the processed frame in a window
        cv2.imshow("Camera 1", img1)
        cv2.imshow("Camera 2", img2)
        
        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("Failed to read frame")

    #     print("Failed to read frames from one or both cameras")

# Release the camera instances and close windows
cap1.release()
cap2.release()
cv2.destroyAllWindows()







