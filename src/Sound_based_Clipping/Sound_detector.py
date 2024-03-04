# import subprocess
# import os
# import sys
# import datetime
# import time
# import VideoEditing.VideoEditor as ve

# class SoundDetector:
#     def __init__(self, video_path: str, output_path: str, audio_path: str, stdout_log_file: str, stderr_log_file: str):
#         self.video_path = video_path
#         self.output_path = output_path
#         self.audio_path = audio_path
#         self.stdout_log_file = stdout_log_file
#         self.stderr_log_file = stderr_log_file
#         self.editor = ve.VideoEditor(video_path, output_path, audio_path, stdout_log_file, stderr_log_file)
#         self.editor.Retrieve_Audio()
#         self.audio_clips = []

    

#     def detect_sound(self, threshold: float, min_duration: float, max_duration: float):
#         """
#         Detects sound in the video and saves the clips with sound to a list.
        
#         :param threshold: The minimum sound level to be considered as sound.
#         :param min_duration: The minimum duration of a sound clip.
#         :param max_duration: The maximum duration of a sound clip.
#         """
#         command = ['ffmpeg', '-i', self.video_path, '-af', f"silencedetect=noise={threshold}dB:d={min_duration}", '-f', 'null', '-']
#         with open(self.stdout_log_file, 'a') as output_log, open(self.stderr_log_file, 'a') as error_log:
#             subprocess.run(command, stdout=output_log, stderr=error_log, check=True)
#         with open(self.stderr_log_file, 'r') as error_log:
#             lines = error_log.readlines()
#             for line in lines:
#                 if "silence_start" in line:
#                     start_time = line.split("silence_start: ")[1].split(" ")[0]
#                     end_time = line.split("silence_end: ")[1].split(" ")[0]
#                     duration = datetime.datetime.strptime(end_time, '%H:%M:%S.%f') - datetime.datetime.strptime(start_time, '%H:%M:%S.%f')
#                     duration = duration.total_seconds()
#                     if (duration <= max_duration):
#                         self.audio_clips.append((start_time, end_time))
#         return self.audio_clips


# import librosa
# import librosa.display
# import matplotlib.pyplot as plt
# import numpy as np
# from moviepy.editor import VideoFileClip

# # Extract audio from video
# video_path = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\bbgame.mp4'  # Change this to your video file path
# audio_path = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\extracted_audio.wav'

# # Use moviepy to extract audio
# clip = VideoFileClip(video_path)
# clip.audio.write_audiofile(audio_path)

# # Load the audio file
# y, sr = librosa.load(audio_path)

# # Length of the audio in samples and creating a time array
# length = len(y)
# time = np.linspace(0., length / sr, length)

# # Compute various audio features
# # RMS Energy
# rmse = librosa.feature.rms(y=y)

# # # Spectral Centroid
# # spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
# # # Normalizing the spectral centroid for visual purposes
# # spectral_centroids_norm = librosa.util.normalize(spectral_centroids)

# # # Spectral Rolloff
# # spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

# # # Zero Crossings
# # zero_crossings = librosa.zero_crossings(y, pad=False)
# # zero_crossings_times = time[zero_crossings]

# # Harmonics
# # harmonic, percussive = librosa.effects.hpss(y)

# # # Pitch (using the mean frequency over time)
# # pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
# # pitch_times = np.linspace(0, length/sr, pitches.shape[1])
# # pitch = np.max(pitches, axis=0)
# # pitch = librosa.util.normalize(pitch)

# # Plotting
# plt.figure(figsize=(15, 10))

# # Amplitude plot
# plt.subplot(2, 2, 1)
# plt.plot(time, y)
# plt.title('Amplitude')
# plt.xlabel('Time (s)')

# # # Pitch plot
# # plt.subplot(3, 2, 2)
# # plt.plot(pitch_times, pitch)
# # plt.title('Pitch')
# # plt.xlabel('Time (s)')

# # RMS Energy plot
# plt.subplot(2, 2, 2)
# frames = range(len(rmse[0]))
# t = librosa.frames_to_time(frames, sr=sr)
# plt.plot(t, rmse[0])
# plt.title('RMS Energy')
# plt.xlabel('Time (s)')

# # # Zero Crossings plot
# # plt.subplot(3, 2, 4)
# # plt.scatter(zero_crossings_times, np.zeros_like(zero_crossings_times), alpha=0.5)
# # plt.title('Zero Crossings')
# # plt.xlabel('Time (s)')

# # # Spectral Features plot
# # plt.subplot(3, 2, 5)
# # plt.plot(time, spectral_centroids_norm, label='Spectral Centroid')
# # plt.plot(time, librosa.util.normalize(spectral_rolloff), label='Spectral Rolloff')
# # plt.title('Spectral Features')
# # plt.xlabel('Time (s)')
# # plt.legend()

# # # Harmonics plot
# # plt.subplot(3, 2, 6)
# # plt.plot(time, harmonic)
# # plt.title('Harmonics')
# # plt.xlabel('Time (s)')

# plt.tight_layout()
# plt.show()


# import librosa
# import numpy as np
# from moviepy.editor import VideoFileClip

# def seconds_to_hms(seconds):
#     """Convert seconds to HH:MM:SS format."""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = int(seconds % 60)
#     return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# def extract_highlights(video_path, audio_path=r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\extracted_audio.wav', interval=5, num_timestamps=100):
#     # Extract audio from the video
#     clip = VideoFileClip(video_path)
#     clip.audio.write_audiofile(audio_path, logger=None)  # logger=None to suppress verbose output

#     # Load the audio file
#     y, sr = librosa.load(audio_path)

#     # Calculate the total duration in seconds
#     total_duration = librosa.get_duration(y=y, sr=sr)

#     # Initialize lists to hold highlights
#     amp_highlights = []
#     rms_highlights = []

#     # Process audio in 5-second chunks
#     for start in np.arange(0, total_duration, interval):
#         end = start + interval
#         if end > total_duration:
#             end = total_duration
#         start_sample = librosa.time_to_samples(start, sr=sr)
#         end_sample = librosa.time_to_samples(end, sr=sr)
        
#         # Extract chunk
#         chunk = y[start_sample:end_sample]
        
#         # Calculate amplitude and RMS energy for the chunk
#         amplitude = np.abs(chunk)
#         rms_energy = librosa.feature.rms(y=chunk)[0]
        
#         # Calculate mean and standard deviation for the chunk
#         amp_mean, amp_std = np.mean(amplitude), np.std(amplitude)
#         rms_mean, rms_std = np.mean(rms_energy), np.std(rms_energy)
        
#         # Check if any point in the chunk is 2 std deviations above the mean
#         if np.any(amplitude > amp_mean + 16 * amp_std):
#             amp_highlights.append(start)
#         if np.any(rms_energy > rms_mean + 4 * rms_std):
#             rms_highlights.append(start)

#     # Convert start times to HH:MM:SS
#     amp_highlights_hms = [seconds_to_hms(t) for t in amp_highlights]
#     rms_highlights_hms = [seconds_to_hms(t) for t in rms_highlights]

#     # Select up to num_timestamps highlights
#     time_amp_selected = amp_highlights_hms[:num_timestamps] if len(amp_highlights_hms) > num_timestamps else amp_highlights_hms
#     time_rms_selected = rms_highlights_hms[:num_timestamps] if len(rms_highlights_hms) > num_timestamps else rms_highlights_hms

#     return time_amp_selected, time_rms_selected

# # Example usage
# video_path = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\bbgame.mp4'  # Change this to your actual video file path
# amp_highlights, rms_highlights = extract_highlights(video_path)

# print("Amplitude Highlights:", amp_highlights)
# print("RMS Energy Highlights:", rms_highlights)

import numpy as np
import moviepy.editor
import math
import matplotlib.pyplot as plt
import VideoEditing.VideoEditor as ve

class ExcitementExtract:
    """Class for analyzing video excitement based on scene cuts, motion, and sound volume."""
    
    def __init__(self, filename):
        """Initialize the video clip and analysis parameters."""
        self.clip = moviepy.editor.VideoFileClip(filename, target_resolution=(240, None))
        self.luminosities = []
        self.threshold = 10.0
        self.fps = 10.0
        self.avg_motion_list = []
        self.cut_density_list = []
        self.sound_list = []
        self.excite_curve = []

        print('File read:', filename)

    def process_frames(self):
        """Process video frames to analyze movement, cuts, and sound."""
        last_fr = None
        for f in self.clip.iter_frames(fps=self.fps, dtype='uint32'):
            
            self.luminosities.append(f.sum())
            
            if last_fr is not None:
                fr_diff = f - last_fr
                self.avg_motion_list.append(fr_diff.sum())
            last_fr = f.copy()

        self.luminosities = np.array(self.luminosities, dtype=float)
        lum_diffs = np.abs(np.diff(self.luminosities))
        avg = lum_diffs.mean()
        luminosity_jumps = 1 + np.array(np.nonzero(lum_diffs > self.threshold * avg))[0]
        if self.clip is not None:
            end = self.clip.duration
        else:
            end = len(self.luminosities) / self.fps
        # end = self.clip.duration
        cuts_list = [0] + list((1.0 / self.fps) * luminosity_jumps) + [end]

        for i in range(1, int(math.ceil(self.clip.duration * self.fps))):
            self.cut_density_list.append(math.exp((1 - (self.next_cut(i / self.fps, cuts_list) - 
                                                       self.prev_cut(i / self.fps, cuts_list))) / 100))

        cut = lambda i: self.clip.audio.subclip(i / self.fps, (i + 1) / self.fps).to_soundarray(fps=22000)
        volume = lambda array: np.sqrt(((1.0 * array) ** 2).mean())
        self.sound_list = [volume(cut(i)) for i in range(0, int(self.fps * (self.clip.duration)))]

        self.scale_curve()

        print('Video processed!')

    def scale_curve(self):
        """Scale the values of arrays between 0 to 100."""
        self.cut_density_list = self._scale_curve(np.asarray(self.cut_density_list))
        self.avg_motion_list = self._scale_curve(np.asarray(self.avg_motion_list))
        self.sound_list = self._scale_curve(np.asarray(self.sound_list))

    @staticmethod
    def _scale_curve(unscaled_arr):
        """Helper method for scaling."""
        max_val = max(unscaled_arr)
        return unscaled_arr * 100 / max_val

    def next_cut(self, f_time, cuts_frame_time):
        """Get the time of the next cut after a given frame."""
        for j in cuts_frame_time:
            if j - f_time > 0:
                return j
        return f_time

    def prev_cut(self, f_time, cuts_frame_time):
        """Get the time of the previous cut before a given frame."""
        for k in reversed(cuts_frame_time):
            if k - f_time < 0:
                return k
        return f_time

    def process_highlights(self):
        """Form the final curve used for highlights extraction."""
        # multiply_orig_curves = [self.cut_density_list[k] * self.avg_motion_list[k] * self.sound_list[k] 
        #                         for k in range(len(self.cut_density_list))]
        multiply_orig_curves = [self.sound_list[k] 
                                for k in range(len(self.cut_density_list))]
        
        kaiser_small_window = np.kaiser(len(self.cut_density_list) // 50, 10)
        multiply_orig_smooth = np.convolve(kaiser_small_window / kaiser_small_window.sum(), 
                                           multiply_orig_curves, mode='same')
        
        return self.get_final_highlights_time(multiply_orig_smooth)

    def get_final_highlights_time(self, smooth_curve):
        """Detect peaks in the smoothed curve to find highlights."""
        increases = np.diff(smooth_curve)[:-1] >= 0
        decreases = np.diff(smooth_curve)[1:] <= 0
        peaks_position = ((increases & decreases).nonzero()[0])
        peaks_value = smooth_curve[peaks_position]
        peaks_position = peaks_position[peaks_value > np.percentile(peaks_value, 85)]

        # final_peaks_position = [peaks_position[0]]
        # print(len(peaks_position))
        # for fr_num in peaks_position:
        #     if fr_num - final_peaks_position[-1] < 100:
        #         if smooth_curve[fr_num] > smooth_curve[final_peaks_position[-1]]:
        #             final_peaks_position[-1] = fr_num
        #         else:
        #             final_peaks_position.append(fr_num)
        # option2 = [int(frame_num / self.fps) for frame_num in final_peaks_position]
        final_times = [int(frame_num / self.fps) for frame_num in peaks_position]
        return final_times
    
    def get_excited_curve(self):
        """ Create smooth graph to capture excitement trend of the match"""
        kaiser_long_window = np.kaiser(len(self.cut_density_list) // 10, 5)
        cuts_scaled_smooth = np.convolve(kaiser_long_window / kaiser_long_window.sum(), self.cut_density_list, mode='same')
        motion_scaled_smooth = np.convolve(kaiser_long_window / kaiser_long_window.sum(), self.avg_motion_list, mode='same')
        sound_scaled_smooth = np.convolve(kaiser_long_window / kaiser_long_window.sum(), self.sound_list, mode='same')
        self.excite_curve = [cuts_scaled_smooth[k] * motion_scaled_smooth[k] * sound_scaled_smooth[k] for k in range(len(self.cut_density_list))]
        self.excite_curve = self._scale_curve(np.asarray(self.excite_curve))
        return self.excite_curve

def _sec_to_hms(seconds):
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def sec_to_hms(seconds):
    """Convert seconds to HH:MM:SS format."""
    
    for i in range(len(seconds)):
        seconds[i] = list(seconds[i])
        seconds[i][0] = _sec_to_hms(seconds[i][0])
        seconds[i][1] = _sec_to_hms(seconds[i][1])
        seconds[i] = tuple(seconds[i])
    return seconds

def get_timestamps(highlights):
    timestamps = []
    for i in range(len(highlights)):
        timestamps.append((highlights[i] - 15, highlights[i] + 15))
    return timestamps

def format_highlights(highlights):
    formatted_highlights = [highlights[0]]
    for i in range(1, len(highlights)):
        if highlights[i] - highlights[i - 1] - 15 > 15:
            formatted_highlights.append(highlights[i])
    return formatted_highlights

if __name__ == "__main__":
    # Example usage
    video_path = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\bbgame.mp4'  # Change this to your actual video file path
    output_path = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\out.mp4'
    audio_path = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\audio.mp3'
    stdout_log_file = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\stdout_log.txt'
    stderr_log_file = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\stderr_log.txt'
    # video_path = r'C:\Users\devth\OneDrive - purdue.edu\SeniorDesign\Open-Source-Software-Senior-Design-Project\data\output_video.mp4'
    ee = ExcitementExtract(video_path)
    ee.process_frames()
    highlights = ee.process_highlights()
    highlights = format_highlights(highlights)
    timestamps = get_timestamps(highlights)
    timestamps = sec_to_hms(timestamps)
    print("Timestamps:", timestamps)
    Editor = ve.VideoEditor(video_path, output_path, audio_path, stdout_log_file, stderr_log_file)
    Editor.trim_and_combine_clips(timestamps)
    # print("Option 2:", sec_to_hms(option2))
    # excited_curve = ee.get_excited_curve()
    # plt.plot(excited_curve)
    # plt.title('Excitement Curve')
    # plt.xlabel('Frame')
    # plt.ylabel('Excitement Level')  
    # plt.show()
    # print("Excited Curve:", excited_curve)


        