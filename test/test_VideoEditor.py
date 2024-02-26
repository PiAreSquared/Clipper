# import moviepy.editor as mp
import os
import pytest
import os
import subprocess
from src.VideoEditing.VideoEditor import VideoEditor


def CreateTestVdeo(video_path, image_path, stdout_log_file, stderr_log_file):
    # Create a test video
    if not os.path.exists(video_path):
        # Create a test video
        duration = 60
        temp_audio_path = r"data\temp_audio.mp3"
        temp_video_path = r"data\temp_video.mp4"
        with open(stdout_log_file, "a") as output_log_file, open(stderr_log_file, "a") as error_log_file:
            subprocess.run([
                'ffmpeg',
                '-y',  # overwrite output files without asking
                '-f', 'lavfi',
                '-i', f'sine=frequency=1000:duration={duration}',  # sine wave, 1000 Hz for the duration
                temp_audio_path
            ], stdout=output_log_file, stderr=error_log_file)
            subprocess.run([
                'ffmpeg',
                '-y',  # overwrite output files without asking
                '-loop', '1',  # loop the image
                '-i', image_path,  # input image
                '-c:v', 'libx264',  # video codec
                '-t', str(duration),  # output file duration
                '-pix_fmt', 'yuv420p',  # pixel format
                '-vf', 'scale=320:240',  # scale the video to 320x240
                temp_video_path  # output file
            ], stdout=output_log_file, stderr=error_log_file)
            # subprocess.run([
            #     'ffmpeg',
            #     '-y',  # overwrite output files without asking
            #     '-loop', '1',  # loop the image
            #     '-i', image_path,  # input image
            #     '-t', str(duration),  # duration of the output file
            #     '-vf', '[in]scale=320:-2,scroll=vertical=2[out]',  # scale and scroll filter
            #     '-c:v', 'libx264',  # video codec
            #     '-pix_fmt', 'yuv420p',  # pixel format
            #     temp_video_path  # output file
            # ])
            
            subprocess.run([
                'ffmpeg',
                '-y',  # overwrite output files without asking
                '-i', temp_video_path,  # input video file
                '-i', temp_audio_path,  # input audio file
                '-c:v', 'copy',  # copy the video stream
                '-c:a', 'aac',  # audio codec
                '-strict', 'experimental',
                '-shortest',  # finish encoding when the shortest stream ends
                video_path  # output file
            ], stdout=output_log_file, stderr=error_log_file)
        os.remove(temp_audio_path)
        os.remove(temp_video_path)
        # subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30", "-t", "5", video_path])
        print(f"Test video created at {video_path}.")
    else:
        print(f"Test video already exists at {video_path}.")
    

def Test_InpFileNotFound():
    try:
        obj1 = VideoEditor(r"invalid_path.mp4", r"output.mp4", r"audio.mp3", r"stdout_log.txt", r"stderr_log.txt")
    except FileNotFoundError as e:
        assert str(e) == "File not found at invalid_path.mp4."
        print("Test_InpFileNotFound passed.")

def Test_TrimAndCombineClips_EmptyIntervals():
    try:
        # video_editor = VideoEditor(r"C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\input.mp4")
        video_editor.trim_and_combine_clips([])
    except ValueError as e:
        assert str(e) == "Intervals list is empty."
        print("Test_TrimAndCombineClips_EmptyIntervals passed.")
        
def Test_TrimClip_StartTimeGreaterThanEndTime():
    try:
        # video_editor = VideoEditor(r"C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\input.mp4")
        video_editor._trim_clip("00:00:10", "00:00:05", "output.mp4")
    except ValueError as e:
        assert str(e) == "Start time cannot be greater than end time."
        print("Test_TrimClip_StartTimeGreaterThanEndTime passed.")

def Test_TrimClip_IntervalGreaterThanDuration():
    try:
        # video_editor = VideoEditor(r"C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\input.mp4")
        video_editor._trim_clip("00:00:10", "01:00:20", r"data/output.mp4")
    except ValueError as e:
        assert str(e) == "interval limit(s) cannot be greater than the duration of the video."
        print("Test_TrimClip_IntervalGreaterThanDuration passed.")


if __name__ == "__main__":    
    print("Running tests...")
    video_path = r"data\input.mp4"
    output_path = r"data\output_video.mp4"
    audio_path = r"data\audio.mp3"
    image_path = r"data\joeyb.jpeg"
    stdout_log_file = r"data\stdout_log.txt"
    stderr_log_file = r"data\stderr_log.txt"
    CreateTestVdeo(video_path, image_path, stdout_log_file, stderr_log_file)
    # print("Test video created.")
    video_editor = VideoEditor(video_path, output_path, audio_path, stdout_log_file, stderr_log_file)
    Test_InpFileNotFound()
    Test_TrimAndCombineClips_EmptyIntervals()
    Test_TrimClip_StartTimeGreaterThanEndTime()
    Test_TrimClip_IntervalGreaterThanDuration()
    print("All tests passed!")