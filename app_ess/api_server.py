# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import os
import socket
import io
import jwt
import datetime
from PIL import Image
from base64 import encodebytes
from flask import Flask, request, Response, jsonify
from flask_httpauth import HTTPBasicAuth
from tinydb import TinyDB, Query, where
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import start_process


# --- STATUS CODES ---
# 200 OK
# 400 BAD REQUEST
# 401 UNAUTHORIZED
# 403 FORBIDDEN
# 404 NOT FOUND

app = Flask(__name__)  # initialize the application

# app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['SECRET_KEY'] = 'thisisatest1'  # testing only
auth = HTTPBasicAuth()
# host_name = socket.gethostname()  # get the name of the host device
# ip_address = socket.gethostbyname(host_name)  # use this to get the ip
query = Query()

if not os.path.exists('db_data/user_db.json'):  # check if a user database has been generated
    secret_key = os.urandom(12).hex()  # generate a random series of 12 numbers
    user_db = TinyDB('db_data/user_db.json')  # path to the user database
    user_db.insert({"public_id": secret_key, "user": "admin", "password": generate_password_hash("edgess21")})  # add default user


# --- AUTHORISATION ---

# authorisation from https://geekflare.com/securing-flask-api-with-jwt/
def token_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        token = None
        u_db = TinyDB('db_data/user_db.json')  # path to the user database

        if request.headers['x-access-token']:
            token = request.headers['x-access-token']

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            current_user = u_db.search(query.public_id == data['public_id'])
        except:
            return jsonify({'message': 'invalid token'})

        return func(current_user, *args, **kwargs)

    return decorator


@app.route('/api/register', methods=['GET', 'POST'])
def register():
    u_db = TinyDB('db_data/user_db.json')  # path to the user database
    req = request.get_json()
    hashed_pass = generate_password_hash(req['password'], method='sha256')  # get the user entered password & encrypt it
    public_id = os.urandom(12).hex()
    user = u_db.insert({'public_id': public_id, 'user': req['name'], 'password': hashed_pass})
    u_db.close()
    return jsonify({'message': 'user ' + req['name'] + ' added'})


@app.route('/api/login', methods=['GET', 'POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return Response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    u_db = TinyDB('db_data/user_db.json')  # path to the user database
    user = u_db.get(Query()['user'] == auth.username)  # get the details for the user logging in

    if check_password_hash(user['password'], auth.password):
        token = jwt.encode({'public_id': user['public_id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return Response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


# --- HTTP GET ---

@app.route('/api/new_data', methods=['GET'])
@token_required
def get_new_data(self):
    ur_db = TinyDB('db_data/unread_data_db.json')  # path to the unread data database
    all_data = ur_db.all()  # get all unread data to send
    if len(all_data) == 0:
        json_list = {"no data to show": all_data}
    else:
        json_list = {'unread data': all_data}  # add it to a list for json encoding
        # ur_db.drop_table('unread_data')  # when the data has been prepared to send we dont need it so delete the table
        ur_db.truncate()  # clear the database
    return json_list  # send the data


@app.route('/api/unknown_faces', methods=['GET'])
@token_required
def get_unknown_faces(self):
    # get everything from the unknown faces db to send
    # db = TinyDB('../Data/edge_security_db.json')  # path to the database
    # ui_table = db.table('unknown_image')  # table with unknown image info
    ui_db = TinyDB('db_data/unknown_image_db.json')  # path to the unknown image database
    unknown_list = []
    for row in ui_db:  # id doesnt show up automatically so need to add it
        row.update({'id': row.doc_id})
        unknown_list.append(row)
    ui_db.close()
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
@token_required
def get_unknown_face(id):
    # get the unknown face from the db based on the provided id
    ui_db = TinyDB('db_data/unknown_image_db.json')  # path to the unknown image database
    unknown_list = ui_db.get(doc_id=int(id))
    ui_db.close()
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
@token_required
def get_detected_faces(self):
    df_db = TinyDB('db_data/detected_face_db.json')  # path to the detected image database
    detected_list = []
    for row in df_db:  # id doesnt show up automatically so need to add it
        row.update({'id': row.doc_id})
        detected_list.append(row)
    df_db.close()
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
    return json_list, 200


@app.route('/api/detected_face/<id>', methods=['GET'])
@token_required
def get_detected_face(self, id):
    df_db = TinyDB('db_data/detected_face_db.json')  # path to the detected image database
    detected_list = df_db.get(doc_id=int(id))
    df_db.close()
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
    return json_list, 200


# get an image to see if the person can be detected/names
@app.route('/api/get_unknown_image/<file_name>', methods=['GET'])
@token_required
def get_image(self, file_name):
    # get all the facial images from the folder into a list
    face_images_path = 'facial_images'
    images_list = os.listdir(face_images_path)
    for image in images_list:
        if image == file_name:
            image_file = Image.open(face_images_path + "/" + file_name, "r")
            byte_arr = io.BytesIO()
            image_file.save(byte_arr, format='JPEG')
            encode_image = encodebytes(byte_arr.getvalue()).decode('ascii')
            json_list = {'file name': file_name, 'image': encode_image}
            return json_list, 200


@app.route('/api/devices', methods=['GET'])
@token_required
def get_devices(self):
    d_db = TinyDB('db_data/devices_db.json')  # path to the devices database
    device_list = []
    for row in d_db:  # id doesnt show up automatically so need to add it
        row.update({'id': row.doc_id})
        device_list.append(row)
    d_db.close()
    json_list = {'devices': device_list}
    return json_list, 200


@app.route('/api/device/<data>', methods=['GET'])
@token_required
def get_device_id(self, data):
    d_db = TinyDB('db_data/devices_db.json')  # path to the devices database
    if isinstance(data, int):  # check the type received is an int
        if d_db.get(doc_id=int(data)):  # get the device based on id
            device_list = d_db.get(doc_id=int(data))
        if d_db.get(Query()['ip'] == data):  # get the device based on ip
            device_list = d_db.get(Query()['ip'] == data)
    if isinstance(data, str):  # check the type received is a string
        if d_db.get(Query()['device_name'] == data):  # get the device based on name
            device_list = d_db.get(Query()['device_name'] == data)
        if d_db.get(Query()['device_type'] == data):  # get the device based on type
            device_list = d_db.get(Query()['device_type'] == data)
    d_db.close()
    json_list = {'devices': device_list}
    return json_list, 200


# --- HTTP POST ---

@app.route('/api/add_device', methods=['POST'])
@token_required
def add_device(self):
    d_db = TinyDB('db_data/devices_db.json')  # path to the devices database
    req = request.get_json()
    d_db.insert(req)
    d_db.close()
    return "Device added", 200


@app.route('/api/add_devices', methods=['POST'])  # no real need for this more an aesthetic call for multiple devices
@token_required
def add_devices(self):
    d_db = TinyDB('db_data/devices_db.json')  # path to the devices database
    req = request.get_json()
    for device in req['devices']:
        d_db.insert(device)
    d_db.close()
    return "Devices added", 200


@app.route('/api/update_unknown_face/', methods=['POST'])
@token_required
def update_unknown_face(self):
    # get the details from the request
    if len(request.json) > 1:
        name = request.json['name']
        f_id = request.json['id']
        filename = request.json['filename']
    else:
        return "A name and either id or filename is required", 400

    # make sure we have either an id or filename to search with
    if (not f_id) and (not filename):
        return "An id or filename is required", 400

    data_list = get_unknown_file()
    for data in data_list:
        face_id = str(data['id'])
        file_name = data['file_name']
        face_name = data['name']

        if (face_id == f_id) or (filename == file_name):
            f_update = update_file(name, file_name)
            d_update = update_db(name, file_name)
        else:
            return "No id or filename found", 400


@app.route('/api/start_cameras', methods=['POST'])
@token_required
def start_cameras(self):
    # check we have devices setup to start
    d_db = TinyDB('db_data/devices_db.json')  # path to the devices database
    if len(d_db) > 0:
        start_process.start_camera_process()
        return "camera process started"
    else:
        return "Please add a device"


# --- HTTP DELETE ---

@app.route('/api/delete_device/<device_ip>', methods=['DELETE'])
@token_required
def delete_device(self, device_ip):
    d_db = TinyDB('db_data/devices_db.json')  # path to the devices database
    # device_table.update(delete('device_ip'), where('device_ip') = ip)
    # device_table.all()
    d_db.remove(where('ip') == device_ip)
    d_db.close()
    return "Device " + device_ip + " removed", 200


# --- Methods ---

def get_unknown_file():
    # open the file of stored images & create a new array to store data being sent
    # with open('../Data/unknown_images.csv', 'r+') as u:
    #     data_list = u.readlines()
    #     return data_list
    ui_db = TinyDB('db_data/unknown_image_db.json')  # path to the unknown image database
    ui_list = []  # list for the unknown image data
    for row in ui_db:  # id doesnt show up automatically so need to add it
        row.update({'id': row.doc_id})
        ui_list.append(row)
    ui_db.close()
    return ui_list


def get_detected_file():
    # open the file of stored detected faces & create a new array to store data being sent
    with open('db_data/detected_faces.csv', 'r+') as d:
        data_list = d.readlines()
        return data_list


def update_file(name, file_name):
    path = 'facial_images/' + file_name + '.jpg'
    new_path = 'facial_images/' + name + '.jpg'
    if os.path.exists(path):
        os.rename(path, new_path)
        return True
    else:
        return False


def update_db(name, file_name):
    ui_db = TinyDB('db_data/unknown_image_db.json')  # path to the unknown image database
    df_db = TinyDB('db_data/detected_face_db.json')  # path to the detected image database

    ui_db.remove(where('file_name') == file_name)  # image is known so not needed to stored here
    ui_db.close()

    df_db.update({'file_name': name, 'name': name}, query.file_name == file_name)
    df_db.close()

    return True


if __name__ == '__main__':
    # app.run(host=ip_address, debug=True)  # use the host ip for the api address
    app.run(host='0.0.0.0')  # Docker needs ip to be set to 0 so it binds to all interfaces
