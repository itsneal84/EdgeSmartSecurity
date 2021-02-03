# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import os
import socket
import io
from PIL import Image
from base64 import encodebytes
from flask import Flask, request, Response, jsonify
from tinydb import TinyDB, Query

# initialize the application
app = Flask(__name__)

host_name = socket.gethostname()  # get the name of the host device
ip_address = socket.gethostbyname(host_name)  # use this to get the ip


# --- HTTP GET ---
@app.route('/api/new_data', methods=['GET'])
def get_new_data():
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    ur_table = db.table('unread_data')  # table with unread data
    all_data = ur_table.all()  # get all unread data to send
    json_list = {'unread data': all_data}  # add it to a list for json encoding
    db.drop_table('unread_data')  # when the data has been prepared to send we dont need it so delete the table
    return json_list  # send the data


@app.route('/api/unknown_faces', methods=['GET'])
def get_unknown_faces():
    # get everything from the unknown faces db to send
    query = Query()
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    ui_table = db.table('unknown_image')  # table with unknown image info
    unknown_list = []
    for row in ui_table:  # id doesnt show up automatically so need to add it
        row.update({'id': row.doc_id})
        unknown_list.append(row)

    # -- ORIGINAL WAY USING CSV --
    # get the array of data to be sent sent
    # data_list = get_unknown_file()
    # unknown_list = []
    # for line in data_list:
    #     if len(data_list) <= 1:  # check if the list is empty
    #         unknown_list.append("No data")
    #         break
    #     face_id, file_name, face_name, date_found, time_found = line.split(',')
    #     if face_id != 'id':
    #         image_list = {'id': face_id, 'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
    #         unknown_list.append(image_list)

    json_list = {'unknown face': unknown_list}
    return json_list


@app.route('/api/unknown_face/<id>', methods=['GET'])
def get_unknown_face(id):
    # get the unknown face from the db based on the provided id
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    ui_table = db.table('unknown_image')  # table with unknown image info
    unknown_list = ui_table.get(doc_id=int(id))

    # -- ORIGINAL WAY USING CSV --
    # get the list of data from the csv file
    # data_list = get_unknown_file()
    # unknown_list = []
    # for line in data_list:
    #     if len(data_list) <= 1:
    #         unknown_list.append("ID not found")
    #         break
    #     face_id, file_name, face_name, date_found, time_found = line.split(',')
    #     if face_id == id:
    #         image_list = {'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
    #         unknown_list.append(image_list)

    json_list = {'unknown face': unknown_list}
    return json_list


@app.route('/api/detected_faces', methods=['GET'])
def get_detected_faces():
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    df_table = db.table('detected_face')  # table with detected image info
    detected_list = []
    for row in df_table:  # id doesnt show up automatically so need to add it
        row.update({'id': row.doc_id})
        detected_list.append(row)

    # -- ORIGINAL WAY USING CSV --
    # get the array of data to be sent sent
    # data_list = get_detected_file()
    # detected_list = []
    # for line in data_list:
    #     if len(data_list) <= 1:
    #         detected_list.append("No data")
    #         break
    #     face_id, file_name, face_name, date_detected, time_detected = line.split(',')
    #     if face_id != 'id':
    #         image_list = {'id': face_id, 'file name': file_name, 'name': face_name, 'date detected': date_detected, 'time detected': time_detected}
    #         detected_list.append(image_list)
    json_list = {'detected faces': detected_list}
    return json_list


@app.route('/api/detected_face/<id>', methods=['GET'])
def get_detected_face(id):
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    df_table = db.table('detected_face')  # table with detected image info
    detected_list = df_table.get(doc_id=int(id))

    # -- ORIGINAL WAY USING CSV --
    # get the list of data from the csv file
    # data_list = get_detected_file()
    # detected_list = []
    # for line in data_list:
    #     face_id, file_name, face_name, date_found, time_found = line.split(',')
    #     if face_id == id:
    #         image_list = {'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
    #         detected_list.append(image_list)
    #     else:
    #         detected_list.append("ID not found")
    #         break

    json_list = {'detected face': detected_list}
    return json_list


# get an image to see if the person can be detected/names
@app.route('/api/get_unknown_image/<file_name>', methods=['GET'])
def get_image(file_name):
    # get all the facial images from the folder into a list
    face_images_path = '../Facial Images'
    images_list = os.listdir(face_images_path)
    for image in images_list:
        if image == file_name:
            image_file = Image.open(face_images_path + "/" + file_name, "r")
            byte_arr = io.BytesIO()
            image_file.save(byte_arr, format='JPEG')
            encode_image = encodebytes(byte_arr.getvalue()).decode('ascii')
            json_list = {'file name': file_name, 'image': encode_image}
            return json_list


# --- HTTP POST ---

@app.route('/api/add_device', methods=['POST'])
def add_device():
    db = TinyDB('../Data/edge_security_db.json')  # path to the database
    device_table = db.table('device')  # table with device info
    req = request.get_json()
    device_table.insert(req)
    return "Device added", 200

# @app.route('/api/set_features/<device_ip>', methods=['POST'])
# def set_motion(ip):


@app.route('/api/update_unknown_face/<id>', methods=['POST'])
def update_unknown_face(f_id):
    # update the name for a unknown image from an id
    name = request.json['name']
    data_list = get_unknown_file()
    for data in data_list:
        face_id, file_name, face_name, date_detected, time_detected = data.split(',')
        if face_id == f_id:
            face_name = name


# @app.route('/api/update_unknown_face/<filename>', methods=['POST'])
# def update_unknown_face(filename):
#     # update the name for a unknown image from an id
#     name = request.json['name']
#     data_list = get_unknown_file()
#     for data in data_list:
#         count = 0
#         face_id, file_name, face_name, date_detected, time_detected = data.split(',')
#         if file_name == filename:
#             pass
#         count += 1
#     if os.path.exists(filename):
#         os.rename(filename, name)


# --- Methods ---

def get_unknown_file():
    # open the file of stored images & create a new array to store data being sent
    with open('../Data/unknown_images.csv', 'r+') as u:
        data_list = u.readlines()
        return data_list


def get_detected_file():
    # open the file of stored detected faces & create a new array to store data being sent
    with open('../Data/detected_faces.csv', 'r+') as d:
        data_list = d.readlines()
        return data_list


if __name__ == '__main__':
    app.run(host=ip_address, debug=True)  # use the host ip for the api address
