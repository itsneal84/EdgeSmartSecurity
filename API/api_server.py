from flask import Flask, request, Response

# initialize the application
app = Flask(__name__)


# --- HTTP GET ---

@app.route('/api/unknown_faces', methods=['GET'])
def get_unknown_faces():
    # get the array of data to be sent sent
    data_list = get_unknown_file()
    unknown_list = []
    for line in data_list:
        face_id, file_name, face_name, date_found, time_found = line.split(',')
        if face_id != 'id':
            image_list = {'id': face_id, 'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
            unknown_list.append(image_list)
    return {'unknown faces': unknown_list}


@app.route('/api/unknown_face/<id>', methods=['GET'])
def get_unknown_face(id):
    # get the list of data from the csv file
    data_list = get_unknown_file()
    for line in data_list:
        face_id, file_name, face_name, date_found, time_found = line.split(',')
        if face_id == id:
            image_list = {'file name': file_name, 'name': face_name, 'date found': date_found, 'time found': time_found}
            return image_list


def get_unknown_file():
    # open the file of stored images & create a new array to store data being sent
    with open('../Storage/unknown_images.csv', 'r+') as f:
        data_list = f.readlines()
        return data_list


# --- HTTP POST ---
@app.route('/api/unknown_face/<id>', methods=['GET'])
def update_unknown_face(id):
    return None


if __name__ == '__main__':
    app.run(debug=True)
