# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

from pathlib import Path
import os


# create the directories & empty files for storage if not already
# https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
def add_files():
    if os.path.exists("../Data"):
        "Directory exists"
    else:
        Path("../Data").mkdir(parents=True, exist_ok=True)

    if os.path.exists("../Live Camera/Facial Images"):
        "Directory exists"
    else:
        Path("../Live Camera/Facial Images").mkdir(parents=True, exist_ok=True)

    if os .path.exists("../Data/detected_faces.csv"):
        "File exists"
    else:
        detected_faces_csv = "../Data/detected_faces.csv"
        os.makedirs(os.path.dirname(detected_faces_csv), exist_ok=True)
        with open(detected_faces_csv, "w") as f:
            f.write("id,file_name,name,date_detected,time_detected")

    if os.path.exists("../Data/unknown_images.csv"):
        "File exists"
    else:
        unknown_images_csv = "../Data/unknown_images.csv"
        os.makedirs(os.path.dirname(unknown_images_csv), exist_ok=True)
        with open(unknown_images_csv, "w") as f:
            f.write("id,file_name,name,date_found,time_found")
