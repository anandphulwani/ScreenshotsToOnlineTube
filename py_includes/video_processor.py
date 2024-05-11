import datetime
import os
import shutil
import subprocess
import threading
import time
import re
import socket
import subprocess
import tempfile
import imagehash
import win32gui
import win32con
from PIL import Image, ImageDraw
from PyQt5.QtCore import QTimer
from .time_checker import TimeChecker

class VideoProcessor:
    # Define regex patterns as class attributes
    DATE_PATTERN = re.compile(r'^\d{4}_\d{2}_\d{2}$')
    HOUR_PATTERN = re.compile(r'^\d{2}$')
    FILENAME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}_\d{2}\.\d{2}\.\d{2}')
    IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']

    def __init__(self, app_instance, app_config_manager_instance):
        self.app = app_instance
        self.app_config_manager = app_config_manager_instance

    def upload_videos_recursively(self):
        command = [
                    "node", 
                    "youtube_uploader.js",
                    f"{self.app.usernameInput.text()}", # username
                    f"{self.app.passwordInput.text()}", # password
                    f"{self.app.playlistInput.text()}", # playlist
                    f"{self.app.privacyStatusInput.currentText()}", # privacystatus
                    f"{os.path.normpath(self.app.basePathInput.text())}", # basepath
        ]
        
        thread = threading.Thread(target=self.checkAndHideChromiumWindow, args=("about:blank - Chromium",)) # New Tab - Chromium, YouTube - Chromium
        thread.start()
        
        result = subprocess.run(command, capture_output=True, text=True)
        print("Output:", result.stdout)
        print("Error:", result.stderr)
        # print("ReturnCode:", result.returncode)

        if result.returncode == 0:
            stdout_lines = result.stdout.strip().split('\n')
            last_line = stdout_lines[-1]
            if last_line == "Error: Daily upload limit reached.":
                daily_limit_reached_removed_at = datetime.datetime.now() + datetime.timedelta(hours=24, minutes=30)
                daily_limit_reached_removed_at = int(daily_limit_reached_removed_at.timestamp())
                self.app.dailyLimitReachedUpto.setText(str(daily_limit_reached_removed_at))
                self.app_config_manager.prepare_and_save_settings_from_ui(self.app.ui_components)
            return True
        else:
            return False
    
    def checkAndHideChromiumWindow(self, window_title):
        while True:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                break
            time.sleep(0.05)
            
    def process_screenshots_and_upload_videos(self):
        while self.app.is_processing:
            isTimeMismatch = False
            print("Processing screenshots...")
            time_checker = TimeChecker()
            if time_checker.compare_dates():
                if not self.app.isDailyLimitReached():
                    self.app.startProcessingButton.setText('Stop Processing')
                    if os.path.exists(self.app.basePathInput.text()) and os.path.isdir(self.app.basePathInput.text()):
                        # Check if there are any subdirectories in the base path
                        hasDirectories = False
                        with os.scandir(self.app.basePathInput.text()) as entries:
                            for entry in entries:
                                if entry.is_dir():
                                    hasDirectories = True
                                    break
                        if hasDirectories:
                            self.process_directories(self.app.basePathInput.text())

                        # Check if there are any MP4 files in the base path
                        hasMP4File = False
                        with os.scandir(self.app.basePathInput.text()) as entries:
                            for entry in entries:
                                if entry.is_file() and entry.name.lower().endswith('.mp4'):
                                    hasMP4File = True
                                    break
                        if hasMP4File:
                            if not self.upload_videos_recursively():
                                self.app.is_processing = False
            else:
                print("Time mismatch.")
                isTimeMismatch = True
               
            # Example: Sleep for some time before checking again
            index = 0
            while True:
                if not self.app.is_processing:
                    self.app.startProcessingButton.setText('Start Processing')
                    self.app.enableControls()
                    print("Stopped processing...")
                    break
                else:
                    if self.app.isDailyLimitReached():
                        remaining_seconds = self.app.getDailyLimitReachedTest()
                        hours = (remaining_seconds) // 3600
                        minutes = ((remaining_seconds) % 3600) // 60
                        seconds = ((remaining_seconds) % 3600) % 60
                        result = f'Daily limit reached, will try in {hours:02}:{minutes:02}:{seconds:02}.'
                    else:
                        remaining_seconds = 3600 - index
                        minutes = remaining_seconds // 60
                        seconds = remaining_seconds % 60
                        result = "Time mismatch, " if isTimeMismatch else ""
                        result += f'Sleeping, {minutes:02}:{seconds:02}.'
                        index += 1
                    if remaining_seconds == 0:
                        break
                    self.app.startProcessingButton.setText(result)
                time.sleep(1)

    def remove_duplicate_images_similar(self, image_folder):
        images = sorted(os.listdir(image_folder))
        prev_hash = None
        duplicates = []

        for image_name in images:
            image_path = os.path.join(image_folder, image_name)
            try:
                img = Image.open(image_path)
                img_hash = imagehash.average_hash(img)

                if prev_hash is not None and img_hash == prev_hash:
                    duplicates.append(image_path)
                else:
                    prev_hash = img_hash
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                continue
        
        for duplicate in duplicates:
            os.remove(duplicate)
        return duplicates

    def remove_duplicate_images_exact(self, image_folder):
        images = sorted(os.listdir(image_folder))
        prev_hash = None
        duplicates = []

        for image_name in images:
            image_path = os.path.join(image_folder, image_name)
            try:
                img = Image.open(image_path)
                mask = Image.new("L", img.size, 255)
                draw = ImageDraw.Draw(mask)
                draw.rectangle([1830, 970, 1920, 1028], fill=0)
                img.putalpha(mask)
                
                img_data = img.tobytes()

                if prev_hash is not None and img_data == prev_hash:
                    duplicates.append(image_path)
                else:
                    prev_hash = img_data
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                continue

        for duplicate in duplicates:
            os.remove(duplicate)
        return duplicates

    def create_video_from_image_list(self, image_paths, output_video_path, hour_markers):
        """
        Create a video from a sequence of images in a folder.
        """
        # print(f'{image_paths}')
        # print(f'{output_video_path}')
        
        durationOfImageInSecs = "0.5"
        # Generate a temporary file containing the list of images
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmpfile:
            for img_path in image_paths:
                tmpfile.write(f"file '{img_path}'\n")
                tmpfile.write(f"duration {durationOfImageInSecs}\n")
            tmpfile_path = tmpfile.name

        # Construct the ffmpeg command to use the concat demuxer
        # ffmpeg -f concat -i input.txt -c:v libx264 -r 30 -pix_fmt yuv420p output.mp4
        ffmpeg_command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', tmpfile_path,
            '-c:v', 'libx264',
            '-r', '30',
            '-pix_fmt', 'yuv420p',
            # '-crf', '25',
            # '-crf', '0',
            output_video_path
        ]
        
        
        if len(image_paths) * float(durationOfImageInSecs) > 3600:
            hourlyTimestamp = True
        else:
            hourlyTimestamp = False
            
        # Generate YouTube timestamp description
        description_path = output_video_path.replace('.mp4', '_description.txt')
        with open(description_path, 'w') as description_file:
            description_file.write(f"Timestamps: \n\n")
            for hour, noOfImages in hour_markers:
                # Assuming each image is displayed for `durationOfImageInSecs` seconds
                timestamp = str(datetime.timedelta(seconds=noOfImages * float(durationOfImageInSecs)))
                if not hourlyTimestamp:
                    timestamp = ':'.join(timestamp.split(':')[1:])
                timestamp = timestamp[:timestamp.rfind('.')] if '.' in timestamp else timestamp
                description_file.write(f"{timestamp} - Hour {hour}\n")
        
        try:
            # Execute the ffmpeg command
            subprocess.run(ffmpeg_command, check=True)
            print("Ended command ffmpeg")
        finally:
            # Clean up by removing the temporary file
            os.remove(tmpfile_path)

    def process_directories(self, base_path):
        base_path = base_path.replace('/', os.path.sep).replace('\\', os.path.sep)
        
        past_dates = [
            datetime.datetime.now().strftime('%Y-%m-%d'), 
            (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        ]
        
        for date_dir in os.listdir(base_path):
            if not self.DATE_PATTERN.match(date_dir) or date_dir in past_dates:
                continue
            date_dir_date = datetime.datetime.strptime(date_dir, '%Y_%m_%d')
            if self.app.processedUptoDate.text() != "":
                processed_upto_date = datetime.datetime.strptime(self.app.processedUptoDate.text(), '%Y_%m_%d')
                if date_dir_date < processed_upto_date:
                    print(f"Skipping {date_dir} as it is before {self.app.processedUptoDate.text()}")
                    continue
            
            date_path = os.path.join(base_path, date_dir)
            if not os.path.isdir(date_path):
                continue

            # Process directory for exact duplicate removal and video creation
            self.process_image_directory(date_path, base_path, date_dir, self.remove_duplicate_images_exact, "")
            # Process directory for similar duplicate removal and video creation
            self.process_image_directory(date_path, base_path, date_dir, self.remove_duplicate_images_similar, "_mini")
            shutil.rmtree(date_path)
            
            if self.app.processedUptoDate.text() == "" or date_dir_date > processed_upto_date:
                self.app.processedUptoDate.setText(date_dir)
                self.app_config_manager.prepare_and_save_settings_from_ui(self.app.ui_components)
    
    def process_image_directory(self, date_path, base_path, date_dir, remove_duplicates_method, video_suffix):
        all_images = []
        hour_markers = []

        hour_dirs = sorted(os.listdir(date_path))
        for hour_dir in hour_dirs:
            # print(f'starting on {hour_dir}')
            if not self.HOUR_PATTERN.match(hour_dir):
                continue  # Skip directories that do not match the hour pattern

            hour_path = os.path.join(date_path, hour_dir)
            if not os.path.isdir(hour_path):
                continue

            removed_duplicates = remove_duplicates_method(hour_path)
            print(f"Removed {len(removed_duplicates)} duplicate images.")

            images = sorted(os.listdir(hour_path))
            for img in images:
                if self.FILENAME_PATTERN.match(img) and any(img.endswith(ext) for ext in self.IMAGE_EXTENSIONS):
                    image_path = os.path.join(hour_path, img)
                    all_images.append(image_path)
                    if len(all_images) == 1 or (hour_markers and hour_markers[-1][0] != hour_dir):  # New hour or first image
                        hour_markers.append((hour_dir, len(all_images)-1))

        if all_images:
            hostname = socket.gethostname()
            output_video_path = os.path.join(base_path, f"{hostname}_{date_dir}{video_suffix}.mp4")
            self.create_video_from_image_list(all_images, output_video_path, hour_markers)
            
                