import os
import glob
from pathlib import Path
import pandas as pd
from subprocess import check_output, CalledProcessError, STDOUT
from datetime import datetime, timedelta
from shutil import rmtree, move
import time


def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print("Process time of {}: {:2.4f}s".format(f.__name__, te-ts))
        return result

    return timed


class VideoClipper:
    def __init__(self, video_dir):
        # Parameters
        self.name_format = "Recorder_%Y-%m-%d_%H-%M-%S"
        self.suffix = ".avi"
        self.print_output = False

        # Get list of videos
        video_paths = glob.glob(str(video_dir)+"/**"+self.suffix)

        # Extract basic video information
        self.df = pd.DataFrame()
        self.df["path"] = [Path(video_path) for video_path in video_paths]
        self.df["start_time"] = self.df["path"].apply(self.get_start_time)
        self.df["duration"] = self.df["path"].apply(self.get_duration)
        self.df["end_time"] = self.df["path"].apply(self.get_end_time)

        # Sort by start time
        self.df = self.df.sort_values(by=["start_time"])

    @timeit
    def clip_event(self, event_start_time, event_end_time, output_dir, output_filename, encode):
        # Calculate video clipping conditions
        self.df["use_clip"] = self.df["path"].apply(
            self.use_clip, event_start_time=event_start_time, event_end_time=event_end_time)
        self.df["clip_from_start"] = self.df["path"].apply(
            self.clip_from_start, event_start_time=event_start_time)
        self.df["clip_to_end"] = self.df["path"].apply(
            self.clip_to_end, event_end_time=event_end_time)
        self.df["clip_start_time"] = self.df["path"].apply(
            self.clip_start_time, event_start_time=event_start_time)
        self.df["clip_end_time"] = self.df["path"].apply(
            self.clip_end_time, event_end_time=event_end_time)

        print("Clipping video")
        print(self.df[self.df["use_clip"] == True])

        def run_command(command):
            try:
                output = check_output(command, stderr=STDOUT).decode()
            except CalledProcessError as e:
                output = e.output.decode()
            if self.print_output:
                print(output)

        # Create temporary directory
        if Path("temp").exists():
            rmtree("temp")
        Path("temp").mkdir(parents=True, exist_ok=True)

        # Create video parts
        concat_list_str = ""
        for index, row in self.df.iterrows():
            if row["use_clip"] == False:
                pass
            else:
                # Clip video
                if (row["clip_from_start"] == False) & (row["clip_to_end"] == False):
                    # mid to mid
                    command = ("ffmpeg -i {} -ss {} -to {} -c copy -y temp/part_{}"+self.suffix).format(
                        row["path"],
                        row["clip_start_time"],
                        row["clip_end_time"],
                        index)
                elif (row["clip_from_start"] == False) & (row["clip_to_end"] == True):
                    # mid to end
                    command = ("ffmpeg -i {} -ss {} -c copy -y temp/part_{}"+self.suffix).format(
                        row["path"],
                        row["clip_start_time"],
                        index)
                elif (row["clip_from_start"] == True) & (row["clip_to_end"] == True):
                    # start to end
                    command = ("ffmpeg -i {} -c copy -y temp/part_{}"+self.suffix).format(
                        row["path"],
                        index)
                elif (row["clip_from_start"] == True) & (row["clip_to_end"] == False):
                    # start to mid
                    command = ("ffmpeg -i {} -t {} -c copy -y temp/part_{}"+self.suffix).format(
                        row["path"],
                        row["clip_end_time"],
                        index)
                run_command(command)

                # Append this file to list of videos to concatenate
                concat_list_str += "file '"+str(row["path"])+"'\n"

        # Concatenate video
        with open("temp\\mylist.txt", mode='w') as f:
            f.write(concat_list_str)
        command = "ffmpeg -f concat -safe 0 -i temp\\mylist.txt -c copy -y temp\\concat"+self.suffix
        run_command(command)

        # Encode video
        if (encode == True) | (Path(output_filename).suffix != self.suffix):
            print("Encoding video:", Path(output_dir)/output_filename)
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            command = ("ffmpeg -i temp\\concat"+self.suffix+" -y {}").format(
                str(Path(output_dir)/output_filename)
            )
            run_command(command)
        else:
            print("Skip encoding:", Path(output_dir)/output_filename)
            move("temp\\concat"+self.suffix,
                 str(Path(output_dir)/output_filename))

        # Remove temporary directory
        if Path("temp").exists():
            rmtree("temp")

    def get_start_time(self, path):
        st = datetime.strptime(
            str(path.stem), self.name_format)
        return st

    def get_duration(self, path):
        command = [
            'ffprobe',
            '-v',
            'error',
            '-show_entries',
            'format=duration',
            '-of',
            'default=noprint_wrappers=1:nokey=1',
            str(path)
        ]

        try:
            output = check_output(command, stderr=STDOUT).decode()
        except CalledProcessError as e:
            output = e.output.decode()

        try:
            duration = float(output)
        except ValueError:
            duration = 0

        return duration

    def get_end_time(self, path):
        st = self.get_start_time(path)
        et = st + timedelta(seconds=self.get_duration(path))
        return et

    def use_clip(self, path, event_start_time, event_end_time):
        if (self.get_start_time(path) > event_end_time) | (self.get_end_time(path) < event_start_time):
            return False
        else:
            return True

    def clip_from_start(self, path, event_start_time):
        if self.get_start_time(path) > event_start_time:
            return True
        else:
            return False

    def clip_to_end(self, path, event_end_time):
        if self.get_end_time(path) < event_end_time:
            return True
        else:
            return False

    def clip_start_time(self, path, event_start_time):
        start_sec = (event_start_time -
                     self.get_start_time(path)).total_seconds()
        start_sec = max(start_sec, 0)  # safeguard
        return start_sec

    def clip_end_time(self, path, event_end_time):
        end_sec = (event_end_time -
                   self.get_start_time(path)).total_seconds()
        end_sec = min(end_sec, self.get_duration(path))  # safeguard
        return end_sec
