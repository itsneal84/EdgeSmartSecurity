# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

from flask import Flask, request, Response, jsonify
import os
import csv

# initialize the application
app = Flask(__name__)


# --- HTTP GET ---

@app.route('/api/unknown_faces', methods=['GET'])
def get_unknown_faces():
    # get the array of data to be sent sent
    data_list = get_unknown_file()
    unknown_list = []
    for line in data_list:
        if len(data_list) <= 1:  # check if the list is empty
            unknown_list.append("No data")
            break
        face_id, file_name, face_name, date_found, time_found = line.split(',')
        if face_id != 'id':
            image_list = {'id': face_id, 'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
            unknown_list.append(image_list)
    json_list = {'unknown face': unknown_list}
    return jsonify(json_list)


@app.route('/api/unknown_face/<id>', methods=['GET'])
def get_unknown_face(id):
    # get the list of data from the csv file
    data_list = get_unknown_file()
    unknown_list = []
    for line in data_list:
        if len(data_list) <= 1:
            unknown_list.append("ID not found")
            break
        face_id, file_name, face_name, date_found, time_found = line.split(',')
        if face_id == id:
            image_list = {'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
            unknown_list.append(image_list)
    json_list = {'unknown face': unknown_list}
    return jsonify(json_list)


@app.route('/api/detected_faces', methods=['GET'])
def get_detected_faces():
    # get the array of data to be sent sent
    data_list = get_detected_file()
    detected_list = []
    for line in data_list:
        if len(data_list) <= 1:
            detected_list.append("No data")
            break
        face_id, file_name, face_name, date_detected, time_detected = line.split(',')
        if face_id != 'id':
            image_list = {'id': face_id, 'file name': file_name, 'name': face_name, 'date detected': date_detected, 'time detected': time_detected}
            detected_list.append(image_list)
    json_list = {'detected faces': detected_list}
    return jsonify(json_list)


@app.route('/api/detected_face/<id>', methods=['GET'])
def get_detected_face(id):
    # get the list of data from the csv file
    data_list = get_detected_file()
    detected_list = []
    for line in data_list:
        face_id, file_name, face_name, date_found, time_found = line.split(',')
        if face_id == id:
            image_list = {'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
            detected_list.append(image_list)
        else:
            detected_list.append("ID not found")
            break
    json_list = {'detected face': detected_list}
    return jsonify(json_list)


# --- HTTP POST ---

@app.route('/api/update_unknown_face/<id>', methods=['POST'])
def update_unknown_face(f_id):
    # update the name for a unknown image from an id
    name = request.json['name']
    data_list = get_unknown_file()
    for data in data_list:
        face_id, file_name, face_name, date_detected, time_detected = data.split(',')
        if face_id == f_id:
            face_name = name


@app.route('/api/update_unknown_face/<filename>', methods=['POST'])
def update_unknown_face(filename):
    # update the name for a unknown image from an id
    name = request.json['name']
    data_list = get_unknown_file()
    for data in data_list:
        count = 0
        face_id, file_name, face_name, date_detected, time_detected = data.split(',')
        if file_name == filename:
            line_to_update = {count:[]}
        count += 1
    if os.path.exists(filename):
        os.rename(filename, name)


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


def get_unknown_csv():
    # open the csv of stored images & create a new array to store data being sent
    data_list = []
    with open('../Data/unknown_images.csv', 'r+') as u:
        data = csv.reader(u)
        data_list.extend(data)
        return data_list


def get_detected_csv():
    # open the csv of stored detected faces & create a new array to store data being sent
    data_list = []
    with open('../Data/detected_faces.csv', 'r+') as d:
        data = csv.reader(d)
        data_list.extend(data)
        return data_list


if __name__ == '__main__':
    app.run(debug=True)
