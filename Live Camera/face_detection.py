# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime

# variables for storing the facial images
face_images_path = 'Facial Images'
facial_images = []  # a list of the files in the path
face_names = []  # a list of all the names from the files
face_list = os.listdir(face_images_path)
video = cv2.VideoCapture(0)  # use webcam 0 for video


def get_encoding():
    encoded_list = []
    for img in facial_images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encoded_list.append(encode)
    return encoded_list


def found_unknown_image(face_image):
    with open('../Storage/unknown_images.csv', 'r+') as f:
        data_list = f.readlines()
        image_list = []
        for line in data_list:
            entry = line.split(',')
            image_list.append(entry[0])
        if face_image not in image_list:
            # split the details from the found image file
            face_name, date_found, time_found = face_image.split('_')
            get_face_id = date_found + time_found
            face_id = get_face_id.replace('-', '')
            f.writelines(f'\n{face_id},{face_image},{face_name},{date_found},{time_found}')


def found_known_image(face_image):
    with open('../Storage/detected_faces.csv', 'r+') as f:
        data_list = f.readlines()
        image_list = []
        for line in data_list:
            entry = line.split(',')
            image_list.append(entry[0])
        if face_image not in image_list:
            # split the details from the found image file
            face_name, date_found, time_found = face_image.split('_')
            get_face_id = date_found + time_found
            face_id = get_face_id.replace('-', '')
            f.writelines(f'\n{face_id},{face_image},{face_name},{date_found},{time_found}')


# loop through each frame & compare any found faces with stored images
while True:
    success, img = video.read()
    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # reduce the image size from live frame
    img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

    for face in face_list:
        current_image = cv2.imread(f'{face_images_path}/{face}')
        if current_image is not None:
            facial_images.append(current_image)
            face_names.append(os.path.splitext(face)[0])  # trim the file name to use as detected name
        else:
            break

    # find the face using face_recognition library
    face_in_current_frame = face_recognition.face_locations(img_small)
    encode_current_frame = face_recognition.face_encodings(img_small)

    for encodedFace, faceLocation in zip(encode_current_frame, face_in_current_frame):
        known_faces = get_encoding()
        matched_face = face_recognition.compare_faces(known_faces, encodedFace)
        facial_distance = face_recognition.face_distance(known_faces, encodedFace)
        match_index = np.argmin(facial_distance)
        # box and name matching face
        if matched_face[match_index]:
            name = face_names[match_index]
            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            found_known_image(name)
        else:
            dt = datetime.now()
            time_stamp = dt.strftime('%d-%m-%y_%H-%M')
            new_face = "unknown-face_{}.jpg".format(time_stamp)
            new_face_path = "Facial Images/{}".format(new_face)
            cv2.imwrite(new_face_path, img)
            found_unknown_image(new_face.replace('.jpg', ''))
            face_list.append(new_face)

    cv2.imshow('Live Camera', img)
    cv2.waitKey(1)
