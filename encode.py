import os
import subprocess
import datetime
import sys
from util.bsr import get_bsr_info
from util.logger import setup_logger
from configs import encode_config

# Set up logger for this module
logger = setup_logger(__name__)


def generate_gif(input_video_path, song_title, mapper_info, overlay_text, output_gif_path):
    """
    Generate a GIF from the input video with specified parameters.

    Args:
        input_video_path (str): Path to the input video file.
        song_title (str): Title of the song for labeling.
        mapper_info (str): Information about the mapper.
        overlay_text (str): Text to overlay on the GIF.
        output_gif_path (str): Path to save the generated GIF.

    Returns:
        None
    """
    logger.info(f"Generating GIF from {input_video_path}")

    if not os.path.exists(input_video_path):
        logger.error(f"Input video file not found: {input_video_path}")
        return
    video_width, video_height = get_video_dimensions(input_video_path)
    trimmed_width = video_width - encode_config.TRIM[0] - encode_config.TRIM[2]
    trimmed_height = video_height - \
        encode_config.TRIM[1] - encode_config.TRIM[3]
    scaled_height = int(encode_config.OUTPUT_WIDTH *
                        trimmed_height / trimmed_width)

    ffmpeg_command = [
        'ffmpeg', '-i', input_video_path, '-vf',
        f'crop={trimmed_width}:{trimmed_height}:{encode_config.TRIM[0]}:{encode_config.TRIM[1]},'
        f'scale={encode_config.OUTPUT_WIDTH}:{scaled_height}:flags=lanczos,'
        f'fps={encode_config.FPS},drawtext=fontfile={encode_config.FONT_FILE}:text={overlay_text}:fontsize=24:fontcolor=white:x=(w-tw)/2:y=h-(2*lh),'
        f'drawtext=fontfile={encode_config.FONT_FILE}:text={mapper_info}:fontsize=8:fontcolor=white:x=(w-tw)/2:y=h-(lh)-{encode_config.TEXT_Y_POS},'
        f'split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
        '-ss', '0', '-t', str(encode_config.CUT_DURATION), '-y', output_gif_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError:
        logger.error("Error during GIF creation. Check the ffmpeg command.")
        return


def get_video_dimensions(input_video_path):
    """
    Get the dimensions of the video.

    Args:
        input_video_path (str): Path to the input video file.

    Returns:
        tuple: Width and height of the video.
    """
    ffprobe_command = ['ffprobe', '-v', 'error', '-show_entries',
                       'stream=width,height', '-of', 'csv=p=0', input_video_path]
    try:
        ffprobe_output = subprocess.check_output(
            ffprobe_command).decode('utf-8')
    except subprocess.CalledProcessError:
        logger.error(f"Error getting dimensions for video: {input_video_path}")
        return None

    return map(int, ffprobe_output.split(','))


def main():
    """
    Main function to handle the conversion from video to GIF.
    Reads the video file path from command line argument and processes it accordingly.
    """
    if len(sys.argv) < 2:
        logger.warning("Usage: python script.py <path_to_video>")
        return
    video_file_path = sys.argv[1]
    print(f"Received file path: {video_file_path}")

    base_name = os.path.splitext(os.path.basename(video_file_path))[0]
    map_id, overlay_text = base_name.split("_")
    details = get_bsr_info(map_id)
    song_title = details['曲名']
    mapper_info = "{} - Mapped by {}".format(map_id, details['mapper名'])

    output_gif_path = f"data/works/{datetime.datetime.now():%Y%m%d%H%M%S}_{map_id}_{song_title}.gif"
    os.makedirs(f"data/works", exist_ok=True)
    generate_gif(video_file_path, song_title, mapper_info,
                 overlay_text, output_gif_path)

    # Output paths
    output_gif_path = f"data/gifs/{overlay_text}/{map_id}.gif"
    os.makedirs(f"data/gifs/{overlay_text}", exist_ok=True)
    generate_gif(video_file_path, song_title, mapper_info,
                 overlay_text, output_gif_path)

    logger.info("Conversion completed successfully.")


if __name__ == "__main__":
    main()
