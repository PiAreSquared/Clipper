import moviepy.editor as mpy
import boto3
import numpy as np
import os

NUM_LOUDEST = 12
NUM_BURSTY = 3
GAME_FILEPATH = "path/to/game.mp4"
OUTPUT_FILE = "path/to/output.mp4"
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'processed-games')
OUTPUT_FILE_SUFFIX = os.environ.get('OUTPUT_FILE_SUFFIX', '_highlights')

def cut(i, video_clip, sample_rate):
    return video_clip.audio.subclip(i, i + sample_rate).to_soundarray(fps=22000)


def vcut(t, video_clip):
    return video_clip.subclip(t[0], t[1])


def get_volume(array):
    # array = array.flatten()
    # sum_squares = sum(x ** 2 for x in array)
    # mean = sum_squares / len(array)
    # return mean ** 0.5

    return np.sqrt(((1.0 * array) ** 2).mean())


def is_new_time_range(time_range, time_ranges):
    start, end = time_range
    for t_range in time_ranges:
        if start >= t_range[0] and start <= t_range[1]:
            return False
        if end >= t_range[0] and end <= t_range[1]:
            return False
        if t_range[0] > start and t_range[1] < end:
            return False
    time_ranges.append(time_range)
    return True


def get_loud_and_bursty_moments(video_clip, clip_length=15):
    # Calculate audio volume at regular intervals
    sample_rate = 0.5  # Samples per second
    volume_data = [(0.0, (0, 0))]
    volume_delta = []

    loud_lookback = (2 / 3) * clip_length
    bursty_lookback = (1 / 3) * clip_length
    loud_lookahead = (1 / 3) * clip_length
    bursty_lookahead = (1 / 3) * clip_length

    for i in range(int(video_clip.duration * sample_rate)):
        time = i / sample_rate
        audio_clip = cut(time, video_clip, 1)
        volume = get_volume(audio_clip)
        volume_delta_dp = abs(volume_data[-1][0] - volume)
        volume_data.append((volume, (max(0, time - loud_lookback), min(time + loud_lookahead, video_clip.duration))))
        volume_delta.append((volume_delta_dp, (max(0, time - bursty_lookback), min(time + bursty_lookahead, video_clip.duration))))

    # Show Top 15 timestamps
    loudest_moments = sorted(volume_data, key=lambda data: -data[0])
    bursty_moments = sorted(volume_delta[1:], key=lambda data: -data[0])

    return loudest_moments, bursty_moments


def get_best_moments(loudest_moments, bursty_moments, num_loudest=NUM_LOUDEST, num_bursty=NUM_BURSTY):
    best_moments = []
    clip_time_ranges = []

    for moment in bursty_moments:
        if is_new_time_range(moment[1], clip_time_ranges):
            best_moments.append(moment + ("bursty",))
        if len(best_moments) == num_bursty:
            break

    for moment in loudest_moments:
        if is_new_time_range(moment[1], clip_time_ranges):
            best_moments.append(moment + ("loudest",))
        if len(best_moments) == num_bursty + num_loudest:
            break

    best_moments = sorted(best_moments, key=lambda data: data[1][0])

    return best_moments


def get_final_cut(best_moments, video_clip):
    return mpy.concatenate_videoclips([vcut(moment[1], video_clip) for moment in best_moments])


def main(s3_client, game_filepath=GAME_FILEPATH, output_file=OUTPUT_FILE, output_suffix=OUTPUT_FILE_SUFFIX, clip_length=15, clip_count=15):
    video_clip = mpy.VideoFileClip(game_filepath)
    import time
    start = time.time()
    print('Loaded video')

    loudest_moments, bursty_moments = get_loud_and_bursty_moments(video_clip, clip_length)
    print('Got loudest and bursty moments', time.time() - start)
    print(f"loudest: {loudest_moments[:15]}")
    print(f"bursty:  {bursty_moments[:15]}")
    start = time.time()
    best_moments = get_best_moments(loudest_moments, bursty_moments, clip_count - clip_count // 5, clip_count // 5)
    print('Got best moments', time.time() - start)
    print(f"best: {best_moments}")
    start = time.time()
    final_cut = get_final_cut(best_moments, video_clip)
    print('Got final cut', time.time() - start)
    start = time.time()

    if output_file == "DUMP_TO_S3":
        s3_filepath = game_filepath.split('/')[-1]
        s3_filepath = s3_filepath.split('.')[0] + output_suffix + "." + s3_filepath.split('.')[1]
        os.chdir('/tmp')
        final_cut.write_videofile("/tmp/output.mp4")
        s3_client.upload_file("/tmp/output.mp4", BUCKET_NAME, s3_filepath)
    else:
        os.chdir('/tmp')
        final_cut.write_videofile(output_file, logger=None, codec='libx264')
    print('Wrote video', time.time() - start)

def clip_video(s3_client, bucket, key, clip_length=15, clip_count=15):
    filename = key.split('/')[-1].rsplit('.', 1)[0]

    filepath = f"/tmp/{filename}.mp4"
    s3_client.download_file(bucket, key, filepath)

    main(s3_client, filepath, "DUMP_TO_S3", "", clip_length, clip_count)
