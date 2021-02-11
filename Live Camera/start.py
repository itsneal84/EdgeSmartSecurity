# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

from tinydb import TinyDB
import concurrent.futures
from face_detection import run_detection
from motion_detection import run_motion
from face_motion_detection import run_face_motion


# def start():
#     db = TinyDB('../Data/edge_security_db.json')  # path to the database
#     device_table = db.table('device')  # table with device info
#     all_devices = device_table.all()  # get all the devices in the device table
#     for device in all_devices:  # for each device start a new process
#         multiprocessing.Process(target=camera_management(device))


def camera_management(device_list):
    # get all the details for the device
    device_ip = device_list['ip']
    # device_name = device_list['device_name']
    # device_type = device_list['device_type']
    stream_link = device_list['stream_link']
    motion = device_list['motion']
    face_det = device_list['face_detection']
    if face_det == 'on' and motion == 'on':
        run_face_motion(stream_link, device_ip)
    if face_det == 'on':
        run_detection(stream_link, device_ip)
    if motion == 'on':
        run_motion(stream_link, device_ip)


def start():
    device_list = []
    device_db = TinyDB('../Data/devices_db.json')  # path to the devices database
    all_devices = device_db.all()  # get all the devices in the device table
    if len(all_devices) > 0:
        for device in all_devices:
            device_list.append(device)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(camera_management, device_list)


if __name__ == '__main__':
    start()
