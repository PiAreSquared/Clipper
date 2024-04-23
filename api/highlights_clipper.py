import easyocr
import cv2
import numpy as np
import os
from datetime import datetime
import re
import time
import moviepy.editor as mpy
import boto3


# NUM_LOUDEST = 12
# NUM_BURSTY = 3
GAME_FILEPATH = "path/to/game.mp4"
OUTPUT_FILE = "path/to/output.mp4"
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'processed-games')
OUTPUT_FILE_SUFFIX = os.environ.get('OUTPUT_FILE_SUFFIX', '_highlights')

def vcut(t, video_clip):
    return video_clip.subclip(t[0], t[1])

def cut(start, end, video_clip):
    return video_clip.audio.subclip(start, end)

def logistic_function(t, A=1, k=1, c=0, d=0):
    return A / (1 + np.exp(-k * (t - c))) + d


def get_video(video_path, ocr_reader, clip_length):

    start = time.time()
    cap = cv2.VideoCapture(video_path)
    video_clip = mpy.VideoFileClip(video_path)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) + 1
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    scoreboardFound = False
    rate = 5 # rate at which we want to extract frames i.e. 1 frame per second
    # frames = [i for i in range(1, num_frames) if i % (int(fps) * rate) == 0]
    
    rightScorePast = -1
    leftScorePast = -1
    timePast = -1
    halfPast = -1
    shotClockPast = -1


    rightscoreChecker1 = 0
    rightscoreChecker2 = 0
    rightscoreChecker3 = 0

    leftscoreChecker1 = 0
    leftscoreChecker2 = 0
    leftscoreChecker3 = 0

    deltaScore = 0
    maxVolume = 0
    # volumeDelta = 0
    timeMetric = 0
    shotClockMetric = 0

    highlights = []


    for frame in range(1, num_frames, int(fps) * rate):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        ret, image = cap.read()
        if not ret:
            continue
        crop_img = image[int(height - (height)*.15):height, 0:width]
        timestamp = frame / fps
        # print(timestamp)
        
        if scoreboardFound:
            crop_img = crop_img[top_left[1]-2:bottom_right[1], top_left[0]:bottom_right[0]]
    

        result = ocr_reader.readtext(crop_img, batch_size=5)
        # for x in result:
        #     print(x[1])

        if scoreboardFound:
            leftScore, rightScore, gameTime, half, shotClock = getNumbers(result)
            scored=False
            # print("Left Score: ", leftScore, "Right Score: ", rightScore, "past Left", leftScorePast, "past Right", rightScorePast)
            if (leftScore != -1 and leftScore == leftScorePast + 1):
                leftScorePast = leftScore
            if (rightScore != -1 and rightScore == rightScorePast + 1):
                rightScorePast = rightScore
            if(leftScore != -1 and leftScore < leftScorePast + 4 and leftScore > leftScorePast + 1):
                soundBit = cut(max(0,int(timestamp)-(clip_length-3)), int(timestamp) + 3, video_clip)
                maxVolume = soundBit.max_volume()
                print("Left Score: ", leftScore, "Right Score: ", rightScore, "Time: ", time, "Half: ", half, "Shot Clock: ", shotClock)
                highlights.append([max(0,int(timestamp)-(clip_length-3)),int(timestamp) + 3, maxVolume, gameTime, half, shotClock, leftScore - rightScore, "left"])
                leftScorePast = leftScore
            if(rightScore != -1 and rightScore < rightScorePast + 4 and rightScore > rightScorePast +1):
                soundBit = cut(max(0,int(timestamp)-(clip_length-3)), int(timestamp) + 3, video_clip)
                maxVolume = soundBit.max_volume()
                print("Left Score: ", leftScore, "Right Score: ", rightScore, "Time: ", time, "Half: ", half, "Shot Clock: ", shotClock)
                highlights.append([max(0,int(timestamp)-(clip_length-3)),int(timestamp) + 3, maxVolume, gameTime, half, shotClock, leftScore - rightScore, "right"])
                rightScorePast = rightScore
            if gameTime != -1:
                timePast = gameTime
            if half != -1:
                halfPast = half
            if shotClock != -1:
                shotClockPast = shotClock
            

            if rightscoreChecker1 != -1 and rightscoreChecker1 == rightscoreChecker2 and rightscoreChecker2 == rightscoreChecker3 and rightScore == rightscoreChecker1:
                rightScorePast = rightscoreChecker1
            if leftscoreChecker1 != -1 and leftscoreChecker1 == leftscoreChecker2 and leftscoreChecker2 == leftscoreChecker3 and leftScore == leftscoreChecker1:
                leftScorePast = leftscoreChecker1

            rightscoreChecker3 = rightscoreChecker2
            rightscoreChecker2 = rightscoreChecker1
            rightscoreChecker1 = rightScore

            leftscoreChecker3 = leftscoreChecker2
            leftscoreChecker2 = leftscoreChecker1
            leftscoreChecker1 = leftScore

        if not scoreboardFound:
            top_left, bottom_right = detectScoreboard(result)
        if (top_left != [] and bottom_right != [] and not scoreboardFound):
            scoreboardFound = True
            rightScorePast = 0
            leftScorePast = 0
        # print("--------------------------------")
    
        # cv2.imshow("frame", crop_img)
        # key = cv2.waitKey(0) 
        # if key & 0xFF == ord('n'):
        #    continue
        # elif key & 0xFF == ord('q'):
        #    break
    stop = time.time()
    print(stop-start)
    # print(highlights)
    # for x in highlights:
    #     print("Volume", x[2], "Game Time", x[3], "Half", x[4], "Shot Clock", x[5], "Old Score Differencial", x[7], "New Score", x[6])
    cap.release()
    cv2.destroyAllWindows()

    return highlights

def getNumbers(ocrResult):
    leftScoreIndex = 0
    rightScoreIndex = 3
    halfIndex = 4
    timeIndex = 1
    shotClockIndex = 2
    success=False
    half_matching_re = ".*HALF"

    gameTime = -1
    shotClock = -1
    leftScore = -1
    rightScore = -1
    half = -1

    time_shotclock = r'\s+'

    try:
        if (len(ocrResult) == 5):
            half_match = re.match(half_matching_re, ocrResult[halfIndex][1])
            if half_match is None:
                timeIndex = 0
                shotClockIndex = 1
                leftScoreIndex = 2
                halfIndex = 3
                rightScoreIndex = 4

        # for x in ocrResult:
        #     print(x[1])
        # print("----------------------")

        if (len(ocrResult) == 4):
            time_matching_re = "([0-9]{0,2}[:|.|;]{1}[0-9]{1,2})"
            time_match = re.match(time_matching_re, ocrResult[1][1])
            if time_match is not None:
                try:
                    leftScore = int(ocrResult[0][1])
                    rightScore = int(ocrResult[2][1])
                except:
                    return -1, -1, -1, -1, -1
                half = ocrResult[3][1][0]
                if(half == 'Z'):
                    half = 2
                else:
                    half = int(half)
                timeSplit = re.split(time_shotclock, ocrResult[1][1])

                gameTime = split_text(timeSplit[0])
                if(len(timeSplit) > 1):
                    shotClock = int(timeSplit[1])
                else:
                    shotClock = -1
            else:
                time_match = re.match(time_matching_re, ocrResult[0][1])
                if time_match is not None: 
                    try:
                        leftScore = int(ocrResult[1][1])
                        rightScore = int(ocrResult[3][1])
                    except:
                        return -1, -1, -1, -1, -1
                    half = ocrResult[2][1][0]
                    if(half == 'Z'):
                        half = 2
                    else:
                        half = int(half)
                    timeSplit = re.split(time_shotclock, ocrResult[0][1])
                    gameTime = split_text(timeSplit[0])
                    if(len(timeSplit) > 1):
                        shotClock = int(timeSplit[1])
                    else:
                        shotClock = -1

        if(len(ocrResult) == 5):
            leftScore = int(ocrResult[leftScoreIndex][1])
            rightScore = int(ocrResult[rightScoreIndex][1])
            half = ocrResult[halfIndex][1][0]
            if(half == 'Z'):
                half = 2
            else:
                half = int(half)
            gameTime = split_text(ocrResult[timeIndex][1])
            shotClock = ocrResult[shotClockIndex][1]
    except:
        return -1, -1, -1, -1, -1
    return leftScore, rightScore, gameTime, half, shotClock

def highlightMetric(scoreDiff, gameTime, half, shotClock, volume, maxVolume):
    abs_diff = abs(scoreDiff)
    if (abs_diff > 30):
        abs_diff = 30
    tranformed = -np.log(abs_diff+1)
    normalized_score = (tranformed - (-np.log(31))) / (-np.log(1) - (-np.log(31)))

    normalized_volume = volume / maxVolume

    normalized_shotClock = int(shotClock) / 30

    # print(gameTime)

    try:
        if(half == 1):
            timeLeft = 20*60 - (gameTime.minute*60 + gameTime.second)
        else:
            timeLeft = 20*60 - (gameTime.minute*60 - gameTime.second) + 20*60
    except:
        timeLeft = 0
    
    normalized_time = logistic_function(timeLeft, A=1, k=0.0025, c=40*60/2, d=0)

    # print(normalized_time, timeLeft, normalized_score, normalized_volume)

    score = normalized_time*(1/3) + normalized_score*(1/3) + normalized_volume*(1/3)

    return score


def split_text(time_str):
    separators = [':', '.', ',', ';'] 

    for sep in separators:
        if sep in time_str:
            numbers = re.findall(r'\d+', time_str)

            return datetime(1,1,1,0,int(numbers[0]), int(numbers[1]))            

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

        top_left = np.min(np.vstack((rect_time_np, rect_half_np)), axis=0)
        bottom_right = np.max(np.vstack((rect_time_np, rect_half_np)), axis=0)


        width2 = bottom_right[0] - top_left[0]

        top_left[0] -= width2
        bottom_right[0] += width2
    
    if (time_found and halfFound):
        return top_left.tolist(), bottom_right.tolist()
    else:
        return [], []
      
def clip_video(s3_client, bucket, key=GAME_FILEPATH, clip_length=15, clip_count=15):
    output_suffix=""
# if __name__ == '__main__':
    reader = easyocr.Reader(['en'], model_storage_directory='/tmp/easyocr', user_network_directory='/tmp/easyocr', gpu=False)
    # file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'purdue_vs_michigan_st.mp4')

    filename = key.split('/')[-1].rsplit('.', 1)[0]

    game_filepath = f"/tmp/{filename}.mp4"
    s3_client.download_file(bucket, key, game_filepath)

    start = time.time()
    highlights = get_video(game_filepath, reader, clip_length)
    print('Got highlights', time.time() - start)
    highlightsRanked = []
    video_clip = mpy.VideoFileClip(game_filepath)

    start = time.time()
    maxVolume = max(sub[2] for sub in highlights)
    for x in highlights:
        score = highlightMetric(x[6], x[3], x[4], x[5], x[2], maxVolume)
        highlightsRanked.append([x[0], x[1], score, x[7]])
    print('Got Ranked highlights', time.time() - start)
    left_count = sum(row.count('left') for row in highlightsRanked)
    right_count = sum(row.count('right') for row in highlightsRanked)

    left_num = int((right_count/(left_count + right_count))* clip_count)
    right_num = int((left_count/(left_count + right_count))* clip_count)

    if (left_num + right_num != clip_count):
        if left_num > right_num:
            right_num += 1
        else:
            left_num += 1

    # print(left_num, right_num)

    newHighlights = []
    if len(highlightsRanked) > 10:
        highlightsRanked = sorted(highlightsRanked, key=lambda x: x[2], reverse=True)
        for x in highlightsRanked:
            if x[3] == 'left' and left_num != 0:
                left_num -= 1
                newHighlights.append(x)
            else:
                if(x[3] == 'right' and right_num != 0):
                    right_num -= 1
                    newHighlights.append(x)
            if(left_num == 0 and right_num == 0):
                break
        highlightsRanked = sorted(newHighlights, key=lambda x: x[0])
    
    start = time.time()
    final_cut = mpy.concatenate_videoclips([vcut(moment, video_clip) for moment in highlightsRanked])

    # final_cut.write_videofile("output.mp4")
    print('Got final cut', time.time() - start)

    start = time.time()
    s3_filepath = game_filepath.split('/')[-1]
    s3_filepath = s3_filepath.split('.')[0] + output_suffix + "." + s3_filepath.split('.')[1]
    os.chdir('/tmp')
    final_cut.write_videofile("/tmp/output.mp4")
    s3_client.upload_file("/tmp/output.mp4", BUCKET_NAME, s3_filepath)

    print('Wrote video', time.time() - start)

    