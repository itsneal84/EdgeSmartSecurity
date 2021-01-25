# Neal Nisbet - B00380762 - 2021_Computing Honours Project - COMP10034

import cv2
from datetime import datetime
from tinydb import TinyDB, Query
from time import sleep

video = cv2.VideoCapture(0)  # use webcam 0 for video
ret, first_frame = video.read()  # get the first frame from the video
ret, second_frame = video.read()  # get the second to compare

while True:
    diff = cv2.absdiff(first_frame, second_frame)  # find the absolute difference between the two frames
    if diff is not None:  # if there is a difference convert the frame
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)  # convert to gray to make it easier to find contours
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)  # returns values but only need the second
        dilated = cv2.dilate(thresh, None, iterations=3)
        all_contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # returns values but only need the first

        for contour in all_contours:  # for each found contour add a bounding box
            (x, y, w, h) = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 1500:  # check the contour area so we detect larger objects this can be tweaked
                cv2.rectangle(first_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # cv2.drawContours(frame1, contour, -1, (0, 255, 0), 2)  # draw the contours of the moving images

        # add detected details to database
        db = TinyDB('../Data/edge_security_db.json')  # path to the database
        dt = datetime.now()
        date_detected = dt.strftime('%d-%m-%y')
        time_detected = dt.strftime('%H:%M:%S')
        md_table = db.table('motion_detection')  # table to hold detected motion info
        md_table.insert({"date_detected": date_detected, "time_detected": time_detected})
        db.close()

        sleep(60)  # 1 min delay to reduce the amount of info sent to the database
        # this could be customisable via api post

    cv2.imshow("Motion", first_frame)
    first_frame = second_frame  # assign the value of frame1 in frame2
    ret, second_frame = video.read()

    cv2.waitKey(1)
