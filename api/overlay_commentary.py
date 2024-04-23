import os
from groq import Groq
# import whisper
import ffmpeg
from pathlib import Path
from openai import OpenAI
from moviepy.editor import *
import subprocess
from datetime import datetime
from pydub import AudioSegment
from io import BytesIO

def get_stt(video_path):
    audio_path = video_path.replace(".mp4", ".mp3")
    to_convert = AudioFileClip(video_path)
    to_convert.write_audiofile(audio_path)
    
    client = OpenAI()
    audio_file = open(audio_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
    )
    os.remove(audio_path)
    return transcription


def get_background_noise(volume_data, background_noise_path, clipped_background_noise_path, final_audio_path):
    # get the length of the video
    seconds = len(volume_data)
    # format into MM:SS datetime object
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    length_of_clip = f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
    
    # Clip the background noise to the length of the video
    bg_noise_clip = AudioFileClip(background_noise_path)
    bg_noise_clip = bg_noise_clip.subclip(20, seconds + 20)
    
    adjusted_clips = []
    for second, volume in volume_data:
        audio_clip = bg_noise_clip.subclip(second, second + 1)
        audio_clip = audio_clip.volumex(volume / 4)
        adjusted_clips.append(audio_clip)
    adjusted_audio = concatenate_audioclips(adjusted_clips)
    adjusted_audio.write_audiofile(final_audio_path)
    # Update the background noise to match the volume of the video
    return adjusted_audio
    
    

def get_volume_data(video_path):
    clip = VideoFileClip(video_path)
    audio = clip.audio

    # Calculate volume at 1-second intervals
    volume_data = []
    for i in range(int(clip.duration)):
        audio_clip = audio.subclip(i, i + 1)
        volume = audio_clip.max_volume()
        volume_data.append((i, volume))

    # volume_data = sorted(volume_data, key=lambda x: x[1], reverse=True)
    return volume_data

def format_background_noise():
    pass
    


def get_commentary(video, video_path, old_commentary, commentary_list_1, commentary_list_2):
    client_groq = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    # original_commentary = get_stt(video_path)
    length_of_clip = video.duration
    # length_of_clip = ffmpeg.probe(video_path)["format"]["duration"]
    length_of_clip = str(int(float(length_of_clip) / 60))

    api_prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are two commentators providing live commentary and analysis for a basketball game broadcast. Your commentary should be lively, insightful, exciting, and flow like a conversation between two basketball commentators going back and forth. Use the original snippet of commentary provided to kick off the discussion. THIS IS A VERY IMPORTANT REQUIREMENT: Ensure the full commentary is at least {} minutes in length if read aloud at a natural pace. Format the output clearly labeling each commentator's lines, e.g. Commentator 1: [line] Commentator 2: [line] <|eot_id|><|start_header_id|>user<|end_header_id|> {} <|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    api_prompt = api_prompt.format(length_of_clip, old_commentary)

    output_commentary = client_groq.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": api_prompt,
            }
        ],
        model="llama3-70b-8192",
    )

    output_commentary = output_commentary.choices[0].message.content
    # print(output_commentary)
    # format output commentary
    # Obtain Commentator 1 and Commentator 2 lines
    commentary_lines = output_commentary.split("\n")
    # print("commentary_lines")
    # print(commentary_lines)

    for line in commentary_lines:
        if line.startswith("Commentator 1:") or line.startswith("**Commentator 1:**"):
            commentary_list_1.append(line[15:].strip())
            # commentary_list.append(("Commentator 1", line[15:].strip()))
        elif line.startswith("Commentator 2:") or line.startswith("**Commentator 2:**"):
            commentary_list_2.append(line[15:].strip())
            # commentary_list.append(("Commentator 2", line[15:].strip()))
    # return commentary_list_1, commentary_list_2

def tts(commentary_list_1, commentary_list_2, speech_file_path, destination_path):

    speech_file_path_c1 = speech_file_path + "_commentary_list_1_"
    speech_file_path_c2 = speech_file_path + "_commentary_list_2_"
    speech_file_path_c1_list = []
    speech_file_path_c2_list = []
    for i in range(len(commentary_list_1)):
        speech_file_path_c1_list.append(speech_file_path_c1 + str(i) + ".wav")
        
    for i in range(len(commentary_list_2)):
        speech_file_path_c2_list.append(speech_file_path_c2 + str(i) + ".wav")
    
    # for i in range(len(commentary_list_1)):
    #     f_c1 = open(speech_file_path_c1_list[i], "w")
    #     f_c1.close()
    # for i in range(len(commentary_list_2)):
    #     f_c2 = open(speech_file_path_c2_list[i], "w")
    #     f_c2.close()

    client_openAI = OpenAI()

    for i in range(len(commentary_list_1)):
        response = client_openAI.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=commentary_list_1[i]
        )
        # store each response in new file
        response.stream_to_file(speech_file_path_c1_list[i])

    for i in range(len(commentary_list_2)):
        response = client_openAI.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=commentary_list_2[i]
        )
        response.stream_to_file(speech_file_path_c2_list[i])
        
    # combined_list = [0] * (len(commentary_list_1) + len(commentary_list_2))
    combined_list = []
    if (len(commentary_list_1) == len(commentary_list_2)):
        for i in range(len(commentary_list_1)):
            combined_list.append(speech_file_path_c1_list[i])
            combined_list.append(speech_file_path_c2_list[i])
    elif (len(commentary_list_1) > len(commentary_list_2)):
        for i in range(len(commentary_list_2)):
            combined_list.append(speech_file_path_c1_list[i])
            combined_list.append(speech_file_path_c2_list[i])
        for j in range(len(commentary_list_2), len(commentary_list_1)):
            combined_list.append(speech_file_path_c1_list[j])
    else:
        for i in range(len(commentary_list_1)):
            combined_list.append(speech_file_path_c1_list[i])
            combined_list.append(speech_file_path_c2_list[i])
        for j in range(len(commentary_list_1), len(commentary_list_2)):
            combined_list.append(speech_file_path_c2_list[j])
        
    audio_clips = [AudioFileClip(audio_file) for audio_file in combined_list]

    combined_audio = concatenate_audioclips(audio_clips)
    combined_audio.write_audiofile(destination_path)
    return combined_audio
    
def overlay_commentary(commentary_path, background_noise_path, output_path):
    commentary = AudioSegment.from_mp3(commentary_path)
    background_noise = AudioSegment.from_mp3(background_noise_path)

    # Overlay the background noise with the commentary
    overlayed_audio = commentary.overlay(background_noise)

    # Export the resulting audio to a new MP3 file
    overlayed_audio.export(output_path, format="mp3")
    
def add_commentary_to_video(video, video_path, commentary_path, output_path):
    # Remove the audio from the original video
    
    audio_free_video = video.without_audio()
    temp_path = video_path.replace(".mp4", "_temp.mp4")
    audio_free_video.write_videofile(temp_path)
    no_audio_video = VideoFileClip(temp_path)
    commentary = AudioFileClip(commentary_path)
    # Add the commentary audio to the video
    final_video = no_audio_video.set_audio(commentary)
    final_video.write_videofile(output_path)
    
def add_commentary_to_video(video, video_path, commentary, bg_noise):
    # Remove the audio from the original video
    audio_free_video = video.without_audio()
    
    # combine the commentary and background noise
    combined_audio = CompositeAudioClip([commentary, bg_noise])

    # Add the commentary audio to the video
    final_video = audio_free_video.set_audio(combined_audio)
    final_video.write_videofile(video_path)

def main(input_path, output_path, background_noise_path):
    os.chdir('/tmp')
    video_path = input_path
    destination_path = output_path
    speech_file_path = input_path.replace(".mp4", "_speech_files")
    commentary_without_background_path = input_path.replace(".mp4", "_commentary_without_background.mp3")
    if os.path.exists(commentary_without_background_path):
        os.remove(commentary_without_background_path)
    clipped_background_noise_path = background_noise_path.replace(".mp3", "_clipped.mp3")
    if os.path.exists(clipped_background_noise_path):
        os.remove(clipped_background_noise_path)
    adjusted_background_noise_path = background_noise_path.replace(".mp3", "_adjusted.mp3")
    if os.path.exists(adjusted_background_noise_path):
        os.remove(adjusted_background_noise_path)
    commentary_path = input_path.replace(".mp4", "_commentary.mp3")
    if os.path.exists(commentary_path):
        os.remove(commentary_path)
    current_time = datetime.now()
    print("Getting STT")
    old_commentary = get_stt(video_path)
    # print("Time taken to read text in seconds is: ", (datetime.now() - current_time).total_seconds())
    commentary_list_1 = []
    commentary_list_2 = []
    video = VideoFileClip(video_path)
    print("Getting commentary")
    get_commentary(video, video_path, old_commentary, commentary_list_1, commentary_list_2)
    print("Performing TTS")
    commentary = tts(commentary_list_1, commentary_list_2, speech_file_path, commentary_without_background_path)
    print("Getting volume data")
    volume_data = get_volume_data(video_path)
    print("Getting background noise")
    bg_noise = get_background_noise(volume_data, background_noise_path, clipped_background_noise_path, adjusted_background_noise_path)
    # overlay_commentary(commentary_without_background_path, adjusted_background_noise_path, commentary_path)
    # add_commentary_to_video(video, video_path, commentary_path, destination_path)
    print("Adding commentary to video")
    add_commentary_to_video(video, destination_path, commentary, bg_noise)