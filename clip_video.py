from pathlib import Path
from datetime import datetime
from lib.videoclipper import VideoClipper

if __name__ == '__main__':
    video_dir = Path("input_data")
    output_dir = Path("output_data")
    event_start_time = datetime(2020, 8, 22, 11, 28, 51)
    event_end_time = datetime(2020, 8, 22, 11, 29, 50)

    output_filename = event_start_time.strftime("%Y-%m-%d_%H-%M-%S.mp4")
    vc = VideoClipper(video_dir)

    vc.clip_event(event_start_time, event_end_time,
                  output_dir, output_filename, encode=True)
