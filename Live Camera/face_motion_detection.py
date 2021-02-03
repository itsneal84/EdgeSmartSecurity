# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime
from tinydb import TinyDB, Query


# variables for storing the facial images
face_images_path = '../Facial Images'
facial_images = []  # a list of the files in the path
face_names = []  # a list of all the names from the files
face_list = os.listdir(face_images_path)  # list of all the files in the directory
query = Query()


def get_encoding():
    encoded_list = []
    for img in facial_images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encoded_list.append(encode)
    return encoded_list


def found_unknown_image(face_image):
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    face_name, date_found, time_found = face_image.split('_')
    ui_table = db.table('unknown_image')  # table to hold unknown image info
    ur_table = db.table('unread_data')  # table to hold unread data e.g. new images
    if not ui_table.search(query.file_name == face_image):
        ui_table.insert({"file_name": face_image, "name": face_name, "date_found": date_found, "time_found": time_found})
        ur_table.insert({"type": "unknown image", "details": {"file_name": face_image, "name": face_name, "date_found": date_found, "time_found": time_found}})
        db.close()


def found_known_image(face_image):
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    face_name, date_found, time_found = face_image.split('_')
    dt = datetime.now()
    date_detected = dt.strftime('%d-%m-%y')
    time_detected = dt.strftime('%H:%M:%S')
    df_table = db.table('detected_face')  # table to hold detected image info
    ur_table = db.table('unread_data')  # table to hold unread data e.g. new images
    df_table.insert({"file_name": face_image, "name": face_name, "date_detected": date_detected, "time_detected": time_detected})
    ur_table.insert({"type": "known image", "details": {"file_name": face_image, "name": face_name, "date_detected": date_detected, "time_detected": time_detected}})
    db.close()


def run_face_motion(stream_link):
    # loop through each frame & compare any found faces with stored images
    if stream_link == "0":
        stream_link = int(stream_link)
    video = cv2.VideoCapture(stream_link)  # use webcam 0 for video
    ret, first_frame = video.read()  # get the first frame from the video
    ret, second_frame = video.read()  # get the second to compare
    while True:
        # facial recognition
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

        # motion detection
        diff = cv2.absdiff(first_frame, second_frame)  # find the absolute difference between the two frames
        if diff is not None:  # if there is a difference convert the frame
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)  # convert to gray to make it easier to find contours
            # blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)  # returns values but only need the second
            dilated = cv2.dilate(thresh, None, iterations=3)
            all_contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # returns values but only need the first

            for contour in all_contours:  # for each found contour add a bounding box
                (x, y, w, h) = cv2.boundingRect(contour)
                if cv2.contourArea(contour) > 1500:  # check the contour area so we detect larger objects this can be tweaked
                    cv2.rectangle(first_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # cv2.drawContours(frame1, contour, -1, (0, 255, 0), 2)  # draw the contours of the moving images

            # add detected details to database
            db = TinyDB('../Data/edge_security_db.json')  # path to the database
            dt = datetime.now()
            date_detected = dt.strftime('%d-%m-%y')
            time_detected = dt.strftime('%H:%M:%S')
            md_table = db.table('motion_detection')  # table to hold detected motion info
            ur_table = db.table('unread_data')  # table to hold unread data e.g. new images
            md_table.insert({"date_detected": date_detected, "time_detected": time_detected})
            ur_table.insert({"type": "motion detection", "details": {"date_detected": date_detected, "time_detected": time_detected}})
            db.close()

        cv2.imshow('Live Camera', img)
        cv2.waitKey(1)