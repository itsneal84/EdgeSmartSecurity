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
        df_table = db.table('detected_faces')
        # df_table.insert({"file_name": "", "name": "", "date_detected": "", "time_detected": ""})

        ui_table = db.table('unknown_images')
        # ui_table.insert({"file_name": "", "name": "", "date_found": "", "time_found": ""})

        db.close()
