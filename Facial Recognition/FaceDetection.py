# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import cv2
import numpy as np
import face_recognition
import os
import SendFaceImage
from datetime import datetime

# variables for storing the facial images
face_images_path = 'Facial Images'
facial_images = []
face_names = []
face_list = os.listdir(face_images_path)
video = cv2.VideoCapture(0)  # use webcam 0 for video


# loop through each image in the directory and get the name
# for face in face_list:
#     currentImage = cv2.imread(f'{face_images_path}/{face}')
#     facial_images.append(currentImage)
#     face_names.append(os.path.splitext(face)[0])  # trim the file name to use as detected name


def getEncoding():
    encoded_list = []
    for img in facial_images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encoded_list.append(encode)
    return encoded_list

# loop through each frame & compare any found faces with stored images
while True:
    success, img = video.read()
    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # reduce the image size from live frame
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    for face in face_list:
        currentImage = cv2.imread(f'{face_images_path}/{face}')
        if currentImage is not None:
            facial_images.append(currentImage)
            face_names.append(os.path.splitext(face)[0])  # trim the file name to use as detected name
        else:
            break

    # find the face using face_recognition library
    faceInCurrentFrame = face_recognition.face_locations(imgSmall)
    encodeCurrentFrame = face_recognition.face_encodings(imgSmall)

    for encodedFace, faceLocation in zip(encodeCurrentFrame, faceInCurrentFrame):
        knownFaces = getEncoding()
        matchedFace = face_recognition.compare_faces(knownFaces, encodedFace)
        facialDistance = face_recognition.face_distance(knownFaces, encodedFace)
        matchIndex = np.argmin(facialDistance)
        # box and name matching face
        if matchedFace[matchIndex]:
            name = face_names[matchIndex].upper()
            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            dt = datetime.now()
            time_stamp = dt.strftime('%d-%m-%y_%H-%M')
            new_face = "unknown_face_{}.jpg".format(time_stamp)
            new_face_path = "Facial Images/{}".format(new_face)
            cv2.imwrite(new_face_path, img)
            face_list.append(new_face)
            SendFaceImage.faceDetected(new_face)

    cv2.imshow('Live Camera', img)
    cv2.waitKey(1)