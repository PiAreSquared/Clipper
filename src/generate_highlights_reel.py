import moviepy.editor as mpy
import urllib.parse
import boto3
import numpy as np
import os

NUM_LOUDEST = 12
NUM_BURSTY = 3
GAME_FILEPATH = "path/to/game.mp4"
OUTPUT_FILE = "path/to/output.mp4"
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'processed-games')
OUTPUT_FILE_SUFFIX = os.environ.get('OUTPUT_FILE_SUFFIX', '_highlights')

my_config = boto3.session.Config(
    region_name='us-east-2',
    signature_version='v4',
    # aws_access_key_id=os.environ.get('AWS_ACCESS_KY_ID'),
    # aws_secret_access_key=os.environ.get('AWS_ACCESS_SECRET_KEY'),
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)
s3_client = boto3.client('s3', config=my_config)


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


def get_loud_and_bursty_moments(video_clip):
    # Calculate audio volume at regular intervals
    sample_rate = 0.5  # Samples per second
    volume_data = [(0.0, (0, 0))]
    volume_delta = []

    for i in range(int(video_clip.duration * sample_rate)):
        time = i / sample_rate
        audio_clip = cut(time, video_clip, 1)
        volume = get_volume(audio_clip)
        volume_delta_dp = abs(volume_data[-1][0] - volume)
        volume_data.append((volume, (max(0, time - 10), min(time + 6, video_clip.duration))))
        volume_delta.append((volume_delta_dp, (max(0, time - 5), min(time + 4, video_clip.duration))))

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


def main(game_filepath=GAME_FILEPATH, output_file=OUTPUT_FILE):
    video_clip = mpy.VideoFileClip(game_filepath)
    import time
    start = time.time()
    print('Loaded video')

    loudest_moments, bursty_moments = get_loud_and_bursty_moments(video_clip)
    print('Got loudest and bursty moments', time.time() - start)
    print(f"loudest: {loudest_moments[:15]}")
    print(f"bursty:  {bursty_moments[:15]}")
    start = time.time()
    best_moments = get_best_moments(loudest_moments, bursty_moments)
    print('Got best moments', time.time() - start)
    print(f"best: {best_moments}")
    start = time.time()
    final_cut = get_final_cut(best_moments, video_clip)
    print('Got final cut', time.time() - start)
    start = time.time()

    if output_file == "DUMP_TO_S3":
        s3_filepath = game_filepath.split('/')[-1]
        s3_filepath = s3_filepath.split('.')[0] + OUTPUT_FILE_SUFFIX + s3_filepath.split('.')[1]
        os.chdir('/tmp')
        final_cut.write_videofile("/tmp/output.mp4")
        s3_client.upload_file("/tmp/output.mp4", BUCKET_NAME, s3_filepath)
    else:
        os.chdir('/tmp')
        final_cut.write_videofile(output_file, logger=None, codec='libx264')
    print('Wrote video', time.time() - start)


def create_presigned_url(bucket_name, object_name, expiration=60):
    """Generate a presigned URL to share an S3 object
    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=expiration,
                                                )

    return response


def lambda_handler(event, context):
    import time
    # get s3 file
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    filename = key.split('/')[-1].rsplit('.', 1)[0] + f"-{time.time_ns() // 91749}-{time.time() // 95137}"

    presigned_url = f"/tmp/{filename}.mp4"
    s3_client.download_file(bucket, key, presigned_url)

    # presigned_url = create_presigned_url(bucket, key)

    main(presigned_url, "DUMP_TO_S3")


if __name__ == "__main__":
    # s3_client.download_file("unprocessed-videos", "purdue_vs_michigan_st.mp4", '/tmp/game.mp4')
    main('/workspaces/Open-Source-Software-Senior-Design-Project/src/purdue_vs_michigan_st.mp4', '/tmp/output.mp4')
