import moviepy.editor as mp
import os
import pytest
from src.VideoEditing.VideoEditor import VideoEditor


def Test_InpFileNotFound():
    try:
        VideoEditor(r"invalid_path.mp4")
    except FileNotFoundError as e:
        assert str(e) == "File not found at invalid_path.mp4."

def Test_TrimAndCombineClips_EmptyIntervals():
    try:
        video_editor = VideoEditor(r"C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\input.mp4")
        video_editor.trim_and_combine_clips([], "output.mp4")
    except ValueError as e:
        assert str(e) == "Intervals list is empty."
        
def Test_TrimClip_StartTimeGreaterThanEndTime():
    try:
        video_editor = VideoEditor(r"C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\input.mp4")
        video_editor._trim_clip("00:00:10", "00:00:05", "output.mp4")
    except ValueError as e:
        assert str(e) == "Start time cannot be greater than end time."

def Test_TrimClip_IntervalGreaterThanDuration():
    try:
        video_editor = VideoEditor(r"C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\input.mp4")
        video_editor._trim_clip("00:00:10", "01:00:20", "output.mp4")
    except ValueError as e:
        assert str(e) == "interval limit(s) cannot be greater than the duration of the video."
        
if __name__ == "__main__":
    Test_InpFileNotFound()
    Test_TrimAndCombineClips_EmptyIntervals()
    Test_TrimClip_StartTimeGreaterThanEndTime()
    Test_TrimClip_IntervalGreaterThanDuration()
    print("All tests passed!")