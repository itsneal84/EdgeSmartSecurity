# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np
import socket

from exception import InvalidException
from FaceDetection import


# get the local ip
def GetLocalIp():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

# send new found face via json
@app.route('/api/face_detection', methods=['POST'])
def faceDetected(face_image):
    try:
        req = request.json

        if req.get('image') is None:
            raise InvalidException('Image required')

        # decode base64 string into np array
        npArray = np.frombuffer(base64.b64decode(req['image'].encode('utf-8')), np.uint8)

        # decode image
        img = cv2.imdecode(npArray, cv2.IMREAD_COLOR)

        if img is None:
            raise InvalidException('Unable to parse image')

        response = {'sucess': True, 'status code': 201, 'message': '{} faces detected'.format(face_image), 'data': {'image': face_image}, }


def detect_face(face_image):
    face =