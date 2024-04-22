import easyocr
import cv2
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime
import re
import time


def get_video(video_path, ocr_reader):
    cap = cv2.VideoCapture(video_path)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) + 1
    print("num_frames: ", num_frames, "fps: ", fps)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("height: ", height, "width: ", width)
    scoreboardFound = False
    rate = 5 # rate at which we want to extract frames i.e. 1 frame per second
    frames = [i for i in range(1, num_frames) if i % (int(fps) * rate) == 0]
    for frame in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        ret, image = cap.read()
        crop_img = image[int(height - (height)*.15):height, 0:width]
        if scoreboardFound:
            crop_img = crop_img[top_left[1]-2:bottom_right[1], top_left[0]:bottom_right[0]]
    

        result = ocr_reader.readtext(crop_img)
        for x in result:
            print(x[1])

        if scoreboardFound:
            getNumbers(result)
        print("-----------------------------------------")
        print("Scoreboard:", scoreboardFound)
        if not scoreboardFound:
            top_left, bottom_right = detectScoreboard(result)
        if (top_left != [] and bottom_right != []):
            scoreboardFound = True

    
        cv2.imshow("frame", crop_img)
        key = cv2.waitKey(0)  # Wait indefinitely for a key press
        if key & 0xFF == ord('n'):
           continue  # Continue to the next frame if 'n' is pressed
        elif key & 0xFF == ord('q'):
           break  # Exit the loop if 'q' is pressed

def getNumbers(ocrResult):
    leftScoreIndex = 0
    rightScoreIndex = 3
    halfIndex = 4
    timeIndex = 1
    shotClockIndex = 2
    success=False
    half_matching_re = ".*HALF"

    time_shotclock = r'\s+'

    if (len(ocrResult) == 5):
        half_match = re.match(half_matching_re, ocrResult[halfIndex][1])
        if half_match is None:
            timeIndex = 0
            shotClockIndex = 1
            leftScoreIndex = 2
            halfIndex = 3
            rightScoreIndex = 4

    if (len(ocrResult) == 4):
        time_matching_re = "([0-9]{0,2}[:|.|;]{1}[0-9]{1,2})"
        time_match = re.match(time_matching_re, ocrResult[1][1])
        if time_match is not None:
            leftScore = int(ocrResult[0][1])
            rightScore = int(ocrResult[2][1])
            half = ocrResult[3][1][0]
            if(half == 'Z'):
                half = 2
            else:
                half = int(half)
            timeSplit = re.split(time_shotclock, ocrResult[1][1])

            time = split_text(timeSplit[0])
            if(len(timeSplit) > 1):
                shotClock = int(timeSplit[1])
            else:
                shotClock = -1

            print("Left Score: ", leftScore)
            print("Right Score: ", rightScore)
            print("Half: ", half)
            print("Time: ", time)
            print("Shot Clock: ", shotClock)
        else:
            time_match = re.match(time_matching_re, ocrResult[0][1])
            print(time_match)
            if time_match is not None: 
                leftScore = int(ocrResult[1][1])
                rightScore = int(ocrResult[3][1])
                half = int(ocrResult[2][1][0])
                if(half == 'Z'):
                    half = 2
                else:
                    half = int(half)
                timeSplit = re.split(time_shotclock, ocrResult[0][1])
                print(timeSplit)
                time = split_text(timeSplit[0])
                if(len(timeSplit) > 1):
                    shotClock = int(timeSplit[1])
                else:
                    shotClock = -1

                print("Left Score: ", leftScore)
                print("Right Score: ", rightScore)
                print("Half: ", half)
                print("Time: ", time)
                print("Shot Clock: ", shotClock)


    if(len(ocrResult) == 5):
        leftScore = int(ocrResult[leftScoreIndex][1])
        rightScore = int(ocrResult[rightScoreIndex][1])
        half = ocrResult[halfIndex][1][0]
        if(half == 'Z'):
            half = 2
        else:
            half = int(half)
        time = split_text(ocrResult[timeIndex][1])
        shotClock = ocrResult[shotClockIndex][1]

        print("Left Score: ", leftScore)
        print("Right Score: ", rightScore)
        print("Half: ", half)
        print("Time: ", time)
        print("Shot Clock: ", shotClock)

        return 1


def split_text(time_str):
    separators = [':', '.', ',', ';']  # List of possible separators

    for sep in separators:
        if sep in time_str:
            numbers = re.findall(r'\d+', time_str)

            return datetime(1,1,1,0,int(numbers[0]), int(numbers[1]))            

    # If no separator is found, assume the time is given as a single number representing hours
    return int(time_str), 0

def detectScoreboard(result):
    time_matching_re = "([0-9]{0,2}[:|.|;]{1}[0-9]{1,2})"
    half_matching_re = ".*HALF"
    ocr_threshold = 8
    time_found = False
    halfFound = False

    bbox_half = []
    bbox_time = []
    if (len(result) > ocr_threshold):
        time_found = False
        for (bbox, text, prob) in result:
            if (not time_found):
                bbox_time = bbox
                time_match = re.match(time_matching_re, text)
                if time_match is not None:
                    time_found = True
            if(not halfFound):
                bbox_half = bbox
                halfMatch = re.match(half_matching_re, text)
                if halfMatch is not None:
                    halfFound = True
    if (bbox_time != [] and bbox_half != []):
        rect_time_np = np.array(bbox_time, np.int32)
        rect_half_np = np.array(bbox_half, np.int32)

        # Find the top-left and bottom-right points for the new rectangle
        top_left = np.min(np.vstack((rect_time_np, rect_half_np)), axis=0)
        bottom_right = np.max(np.vstack((rect_time_np, rect_half_np)), axis=0)


        width2 = bottom_right[0] - top_left[0]

        # Extend the rectangle to the left and right
        top_left[0] -= width2
        bottom_right[0] += width2
    
    if (time_found and halfFound):
        return top_left.tolist(), bottom_right.tolist()
    else:
        return [], []
      
if __name__ == '__main__':
    print('Hello')
    reader = easyocr.Reader(['en'])
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'testVideo.mp4')
    get_video(file_path, reader)