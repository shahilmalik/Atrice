from tkinter import E
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

def histogram_equalization(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply histogram equalization
    equalized_image = cv2.equalizeHist(gray_image)

    # Convert the equalized grayscale image back to color
    equalized_color_image = cv2.cvtColor(equalized_image, cv2.COLOR_GRAY2BGR)

    return equalized_color_image

    
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
        #imgc = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
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


def process_frame(img, encodeListKnown, attendance_data, threshold=0.5):
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    # imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    imgS = histogram_equalization(imgS)
    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        minDistance = min(faceDis)
        if minDistance <= threshold:
            closestMatchIndex = np.argmin(faceDis)
            name = classNames[closestMatchIndex].upper()
            print(name)

            if name not in attendance_data:
                attendance_entry = markAttendance(name)
                if attendance_entry:
                    attendance_data.append(name)

            # Draw rectangles and text on the frame
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


cap1 = cv2.VideoCapture(0)
#cap2 = cv2.VideoCapture(1)
while True:
    attendance_data = []
    
    # Read frames from both cameras
    ret1, img1 = cap1.read()
    #ret2, img2 = cap2.read()

    if ret1:
        process_frame(img1, encodeListKnown, attendance_data)
       # process_frame(img2, encodeListKnown, attendance_data)

        if len(attendance_data) > 0:
            print(*attendance_data, sep='\n')

        # Display the processed frames in separate windows
        cv2.imshow("Camera 1", img1)
        #cv2.imshow("Camera 2", img2)
        
        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("Failed to read frames from one or both cameras")

# Release the camera instances and close windows
cap1.release()
#cap2.release()
cv2.destroyAllWindows()



# Load an image

