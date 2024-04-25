import subprocess
import os
import sys
import time
 
def _in_seconds(time_str: str) -> int:
    """
    Converts a time string in 'HH:MM:SS' format to seconds.
    
    :param time_str: The time string in 'HH:MM:SS' format.
    :return: The time in seconds.
    """
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

class VideoEditor:
    def __init__(self, input_video_path: str, output_video_path: str, audio_path: str, stdout_log_file: str, stderr_log_file: str):
        self.input_video_path = input_video_path
        self.stdout_log_file = stdout_log_file
        self.stderr_log_file = stderr_log_file
        self.output_video_path = output_video_path
        self.audio_path = audio_path
        if (not os.path.exists(input_video_path)):
                raise FileNotFoundError(f"File not found at {input_video_path}.")
        self.duration = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video_path]).decode('utf-8').strip()
        # subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video_path]).decode('utf-8').strip()
    
    def get_video_duration(self, video_path: str) -> str:
        with open(self.stdout_log_file, 'w') as stdout, open(self.stderr_log_file, 'w') as stderr:
            video_length = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]).decode('utf-8').strip()
        return video_length
    
    def trim_and_combine_clips(self, intervals: list[tuple[str, str]]):
        """
        Trims the video into individual clips based on the given intervals and combines them into a final video.
        
        :param intervals: A list of tuples where each tuple contains the start and end time in 'HH:MM:SS' format.
        :param output_video_path: The path to save the combined video.
        """
        # Temporary file list to store paths of trimmed clips
        temp_files = []
        
        if (len(intervals) != 0):
            
            # Trim the video into individual clips
            for i, (start, end) in enumerate(intervals):
                temp_file = f"temp_clip_{i}.mp4"
                temp_files.append(temp_file)
                self._trim_clip(start, end, temp_file)
            
            # Combine all the trimmed clips into one video
            self._combine_clips(temp_files)
            
            # Cleanup temporary files
            for temp_file in temp_files:
                os.remove(temp_file)
                # print(f"{temp_file} deleted successfully.")
        else:
            raise ValueError("Intervals list is empty.")
        
    def _trim_clip(self, start_time: str, end_time: str, output_file: str):
        """
        Trims a clip from the video between start_time and end_time.
        
        :param start_time: Start time of the clip in 'HH:MM:SS' format.
        :param end_time: End time of the clip in 'HH:MM:SS' format.
        :param output_file: The output file path for the trimmed clip.
        """
        if (start_time > end_time):
            raise ValueError("Start time cannot be greater than end time.")
        elif (_in_seconds(end_time) > float(self.duration) or _in_seconds(start_time) > float(self.duration)):
            raise ValueError("interval limit(s) cannot be greater than the duration of the video.")
        command = ['ffmpeg', '-i', self.input_video_path, '-ss', start_time, '-to', end_time, '-c', 'copy', output_file]
        with open(self.stdout_log_file, 'a') as output_log, open(self.stderr_log_file, 'a') as error_log:
            subprocess.run(command, stdout=output_log, stderr=error_log, check=True)

    def _combine_clips(self, clip_paths: list[str]):
        """
        Combines all given clips into a single video.
        
        :param clip_paths: A list of paths to the video clips to be combined.
        :param output_video_path: The path to save the combined video.
        """
        with open('files.txt', 'w') as f:
            for clip in clip_paths:
                f.write(f"file '{clip}'\n")
        command = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'files.txt', '-c', 'copy', self.output_video_path]
        with open(self.stdout_log_file, 'a') as output_log, open(self.stderr_log_file, 'a') as error_log:
            subprocess.run(command, stdout=output_log, stderr=error_log, check=True)
        os.remove('files.txt')
        
    def Retrieve_Audio(self):
        command = ['ffmpeg', '-i', self.output_video_path, '-vn', self.audio_path]
        with open(self.stdout_log_file, 'a') as output_log, open(self.stderr_log_file, 'a') as error_log:
            subprocess.run(command, stdout=output_log, stderr=error_log, check=True)
        
    def Remove_Audio(self, output_no_audio_video_path: str):
        command = ['ffmpeg', '-i', self.output_video_path, '-c', 'copy', '-an', output_no_audio_video_path]
        with open(self.stdout_log_file, 'a') as output_log, open(self.stderr_log_file, 'a') as error_log:
            subprocess.run(command, stdout=output_log, stderr=error_log, check=True)

    def Add_Audio(self, input_video_path: str, output_video_path: str):
        video_duration = self.get_video_duration(input_video_path)
        audio_duration = self.get_video_duration(self.audio_path)
        # if (video_duration != audio_duration):
        #     print(f"Video duration: {video_duration}, Audio duration: {audio_duration}")
        #     print(f"Output video duration: {self.get_video_duration(self.output_video_path)}")
        #     raise ValueError("Video and audio duration must be the same.")
        # command = ['ffmpeg', '-i', input_video_path, '-i', self.audio_path, '-c', 'copy', '-map', '0:v:0', '-map', '1:a:0', input_video_path]
        command = ['ffmpeg', '-i', input_video_path, '-i', self.audio_path, '-c', 'copy', '-shortest', output_video_path]
        with open(self.stdout_log_file, 'a') as output_log, open(self.stderr_log_file, 'a') as error_log:
            subprocess.run(command, stdout=output_log, stderr=error_log, check=True)
        
if __name__ == "__main__":
    # Example usage
    video_path = r"data\input.mp4"
    output_path = r"data\output_video.mp4"
    audio_path = r"data\audio.mp3"
    output_path_no_audio = r"data\output_video_no_audio.mp4"
    output_path_with_audio = r"data\output_video_with_audio.mp4"
    stdout_log_file = r"data\stdout_log.txt"
    stderr_log_file = r"data\stderr_log.txt"
    
    if (os.path.exists(output_path)):
        os.remove(output_path)
    if (os.path.exists(audio_path)):
        os.remove(audio_path)
    if (os.path.exists(output_path_no_audio)):
        os.remove(output_path_no_audio)
    if (os.path.exists(output_path_with_audio)):
        os.remove(output_path_with_audio)
    editor = VideoEditor(video_path, output_path, audio_path, stdout_log_file, stderr_log_file)
    intervals = [("00:00:10", "00:00:20"), ("00:00:30", "00:00:40")]
    start_time = time.time()
    editor.trim_and_combine_clips(intervals)
    print(f"Time taken to Trim and Combine: {time.time() - start_time} seconds.")
    editor.Retrieve_Audio()
    start_time = time.time()
    editor.Remove_Audio(output_path_no_audio)
    print(f"Time taken to Remove Audio: {time.time() - start_time} seconds.")
    start_time = time.time()
    editor.Add_Audio(output_path_no_audio, output_path_with_audio)
    print(f"Time taken to Add Audio: {time.time() - start_time} seconds.")