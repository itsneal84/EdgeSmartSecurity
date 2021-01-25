# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import os
from tinydb import TinyDB


def create_db():
    # check the db hasnt already been created
    if os.path.exists('../Data/edge_security_db.json'):
        "db exists"
    else:
        # if not add the tables
        db = TinyDB('../Data/edge_security_db.json')

        df_table = db.table('detected_face')  # table to hold detected face info
        df_table.insert({"file_name": "", "name": "", "date_detected": "", "time_detected": ""})

        ui_table = db.table('unknown_image')  # table to hold unknown image info
        ui_table.insert({"file_name": "", "name": "", "date_found": "", "time_found": ""})

        cd_table = db.table('connected_device')  # table to hold info for connected devices e.g. camera
        cd_table.insert({"device_ip": "", "device_name": ""})

        fet_table = db.table('feature')  # table to what features are being used e.g. facial recognition
        fet_table.insert({"feature": "", "activated": ""})

        db.close()
