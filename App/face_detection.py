# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime
from tinydb import TinyDB, Query


# open()
# 'r' - Read - Default value. Opens a file for reading, error if the file does not exist
# 'a' - Append - Opens a file for appending, creates the file if it does not exist
# 'w' - Write - Opens a file for writing, creates the file if it does not exist
# 'x' - Create - Creates the specified file, returns an error if the file exist
# 't' - Text - Default value. Text mode
# 'b' - Binary - Binary mode (e.g. images)
# '+' - Open a file for updating (reading and writing)

# create the directories & empty files for storage if not already
# setup_files.add_files()
# create_db.create_db()


# variables for storing the facial images
face_images_path = '../Facial Images'
facial_images = []  # a list of the files in the path
face_names = []  # a list of all the names from the files
face_list = os.listdir(face_images_path)  # list of all the files in the directory
query = Query()
# stream_link = 1  # '../Test Video/People in Street.mp4' # testing
# device_ip = "192.168.0.21"  # testing


def get_encoding():
    encoded_list = []
    for img in facial_images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encoded_list.append(encode)
    return encoded_list


def found_unknown_image(face_image, device_ip):
    ui_db = TinyDB('../Data/unknown_image_db.json')  # path to the unknown image database
    ur_db = TinyDB('../Data/unread_data_db.json')  # path to the unread data database
    face_name, date_found, time_found = face_image.split('_')
    if not ui_db.search(query.file_name == face_image):
        ui_db.insert({"file_name": face_image, "name": face_name, "date_found": date_found, "time_found": time_found})
        ur_db.insert({"type": "unknown image", "details": {"device_ip": device_ip, "file_name": face_image, "name": face_name, "date_found": date_found, "time_found": time_found}})
        ui_db.close()
        ur_db.close()

    # -- ORIGINAL VERSION USING CSV --
    # with open('../Data/unknown_images.csv', 'r+') as f:
    #     data_list = f.readlines()
    #     image_list = []
    #     for line in data_list:
    #         entry = line.split(',')
    #         image_list.append(entry[0])
    #     if face_image not in image_list:
    #         # split the details from the found image file
    #         face_name, date_found, time_found = face_image.split('_')
    #         get_face_id = date_found + time_found
    #         face_id = get_face_id.replace('-', '')
    #         f.writelines(f'\n{face_id},{face_image},{face_name},{date_found},{time_found}')


def found_known_image(face_image, device_ip):
    df_db = TinyDB('../Data/detected_face_db.json')  # path to the detected image database
    ur_db = TinyDB('../Data/unread_data_db.json')  # path to the unread data database
    face_name, date_found, time_found = face_image.split('_')
    dt = datetime.now()
    date_detected = dt.strftime('%d-%m-%y')
    time_detected = dt.strftime('%H:%M:%S')
    df_db.insert({"file_name": face_image, "name": face_name, "date_detected": date_detected, "time_detected": time_detected})
    ur_db.insert({"type": "known image", "details": {"device_ip": device_ip, "file_name": face_image, "name": face_name, "date_detected": date_detected, "time_detected": time_detected}})
    df_db.close()
    ur_db.close()

    # -- ORIGINAL VERSION USING CSV --
    # with open('../Data/detected_faces.csv', 'r+') as f:
    #     data_list = f.readlines()
    #     image_list = []
    #     for line in data_list:
    #         entry = line.split(',')
    #         image_list.append(entry[0])
    #     if face_image not in image_list:
    #         # split the details from the found image file
    #         face_name, date_found, time_found = face_image.split('_')
    #         get_face_id = date_found + time_found
    #         face_id = get_face_id.replace('-', '')
    #         f.writelines(f'\n{face_id},{face_image},{face_name},{date_found},{time_found}')


def run_detection(stream_link, device_ip):
    # loop through each frame & compare any found faces with stored images
    video = cv2.VideoCapture(1)  # use webcam 0 for video
    while True:
        success, img = video.read()

        # img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # reduce the image size from live frame
        # img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

        for face in face_list:
            current_image = cv2.imread(f'{face_images_path}/{face}')
            if current_image is not None:
                facial_images.append(current_image)
                face_names.append(os.path.splitext(face)[0])  # trim the file name to use as detected name
            else:
                break

        # find the face using face_recognition library & compare it to the encoded image from the video
        face_in_current_frame = face_recognition.face_locations(img)
        encode_current_frame = face_recognition.face_encodings(img)

        for encodedFace, faceLocation in zip(encode_current_frame, face_in_current_frame):
            known_faces = get_encoding()
            matched_face = face_recognition.compare_faces(known_faces, encodedFace)
            facial_distance = face_recognition.face_distance(known_faces, encodedFace)
            match_index = np.argmin(facial_distance)
            # box matching face
            if matched_face[match_index]:
                name = face_names[match_index]
                y1, x2, y2, x1 = faceLocation
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                found_known_image(name, device_ip)
            else:
                # box found face
                y1, x2, y2, x1 = faceLocation
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # save unknown details
                dt = datetime.now()
                time_stamp = dt.strftime('%d-%m-%y_%H-%M')
                new_face = "unknown-face_{}.jpg".format(time_stamp)
                new_face_path = "../Facial Images/{}".format(new_face)
                cv2.imwrite(new_face_path, img)
                found_unknown_image(new_face.replace('.jpg', ''), device_ip)
                face_list.append(new_face)

        cv2.imshow('Live Camera', img)
        cv2.waitKey(1)


# run_detection(stream_link, device_ip)  # testing
