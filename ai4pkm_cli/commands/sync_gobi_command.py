# 최종 파일 경로: ai4pkm_cli/commands/sync_Gobi_command.py

import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from tzlocal import get_localzone
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai4pkm_cli.config import Config


class SyncGobiCommand:
    def __init__(self, logger):
        self.logger = logger
        self.config = Config()
        self.api_key = os.getenv("GOBI_API_KEY")
        self.gobi_config = self.config.get("gobi_sync", {})
        self.api_base_url = self.gobi_config.get(
            "api_base_url", "https://api.joingobi.com/api"
        )
        self.output_dir = Path(self.gobi_config.get("output_dir", "Ingest/Gobi"))

    def run_sync(self):
        """
        Gobi 데이터 동기화를 실행하는 메인 함수.
        """
        if not self.api_key:
            self.logger.warning(
                "GOBI_API_KEY not found in .env file. Skipping sync command."
            )
            return False

        self.logger.info("Starting Gobi data sync command...")
        try:
            # Check for local_timezone setting first, fallback to get_localzone()
            gobi_config = self.config.get("gobi_sync", {})
            local_timezone_setting = gobi_config.get("local_timezone")
            if local_timezone_setting:
                local_timezone = pytz.timezone(local_timezone_setting)
                timezone_name = local_timezone_setting
                self.logger.info(f"Using configured timezone: {timezone_name}")
            else:
                local_timezone = get_localzone()
                timezone_name = str(local_timezone)
                self.logger.info(f"Using system local timezone: {timezone_name}")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            transcriptions, frames = self.fetch_all_data(timezone_name)

            markdowns = self.format_data_markdown(transcriptions, frames, timezone_name)

            for target_date, markdown in markdowns.items():
                self.save_to_file(markdown, target_date)

            self.logger.info("Gobi data sync command finished successfully.")
            return True
        except Exception as e:
            import traceback

            traceback.print_exc()
            self.logger.error(f"An error occurred during Gobi sync command: {e}")
            return False

    def fetch_all_data(self, timezone_name):
        print("ℹ️  Fetching recent data...")

        last_sync_time_file = self.output_dir / "lastSyncTime.txt"
        if last_sync_time_file.exists():
            with open(last_sync_time_file, "r") as f:
                last_sync_time = int(f.read())
                last_sync_time = int(
                    datetime.fromtimestamp(last_sync_time / 1000).astimezone(pytz.timezone(timezone_name))
                    .replace(hour=0, minute=0, second=0, microsecond=0)
                    .timestamp()
                    * 1000
                )
        else:
            last_sync_time = None

        if last_sync_time:
            params = {"lastSyncTime": last_sync_time}
        else:
            params = {}

        transcriptions = []
        frames = []
        try:
            response = requests.get(
                f"{self.api_base_url}/sync",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            transcription_chunks = data.get("transcriptions", [])
            for transcription in transcription_chunks:
                for line in transcription["transcription"].split("\n"):
                    if not line:
                        continue
                    date_time_str = ":".join(line.split(":")[:-1])
                    speaker = date_time_str.split("@")[0]
                    date_time_str = date_time_str.split("@")[1][:-6] + "Z"
                    date_time_str = datetime.fromisoformat(
                        date_time_str.replace("Z", "+00:00")
                    )
                    date_time_str = date_time_str.strftime("%Y-%m-%dT%H:%M:%SZ")
                    transcriptions.append(
                        {
                            **transcription,
                            "transcription": line.split(": ")[-1],
                            "created_at": date_time_str,
                            "speaker": speaker,
                        }
                    )
            frames.extend(data.get("frames", []))
            lastSyncTime = data.get("lastSyncTime")
            with open(self.output_dir / "lastSyncTime.txt", "w+") as f:
                f.write(str(lastSyncTime))

        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            if hasattr(e.response, "text"):
                print(f"Response: {e.response.text}")
            return [], []

        print(
            f"✅ Retrieved {len(transcriptions)} transcriptions and {len(frames)} frames."
        )
        return transcriptions, frames

    def _download_frame(self, download_url, file_path):
        """
        Downloads a single frame image to the specified path.
        Returns True if successful, False otherwise.
        """
        try:
            if not file_path.exists():
                self.logger.info(f"Downloading frame to {file_path}...")
                response = requests.get(download_url)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
            return True
        except Exception as e:
            self.logger.error(f"Failed to download frame {file_path}: {e}")
            return False

    def _process_entry(self, entry, local_tz):
        """
        Processes a single entry (transcription or frame) and returns the formatted data.
        Returns a tuple of (date_key, markdown_line, download_task_or_None).
        """
        transcription = entry.get("transcription")
        download_url = entry.get("downloadUrl")
        timestamp = entry.get("created_at")
        speaker = entry.get("speaker")

        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        local_dt = dt.astimezone(local_tz)
        date_key = local_dt.strftime("%Y-%m-%d")

        if transcription:
            markdown_line = (
                f"{local_dt.strftime('%Y-%m-%d %H:%M:%S')} {speaker}: {transcription}\n"
            )
            return date_key, markdown_line, None
        elif download_url:
            filename = f"{timestamp.split('T')[1].split('.')[0]}.jpeg"
            # Create hierarchical folder structure: frames/YYYY/mm/dd/HH
            year = local_dt.strftime("%Y")
            month = local_dt.strftime("%m")
            day = local_dt.strftime("%d")
            hour = local_dt.strftime("%H")

            relative_dir = f"./frames/{year}/{month}/{day}/{hour}"
            frames_dir = self.output_dir / relative_dir
            frames_dir.mkdir(parents=True, exist_ok=True)
            file_path = frames_dir / filename

            markdown_line = f"{local_dt.strftime('%Y-%m-%d %H:%M:%S')} ![frame]({relative_dir}/{filename})\n"
            download_task = (download_url, file_path)
            return date_key, markdown_line, download_task

        return None, None, None

    def format_data_markdown(self, transcriptions, frames, timezone_str):
        """
        Converts lifelog data to the exact markdown format used by the Obsidian plugin.
        """
        data = transcriptions + frames

        local_tz = pytz.timezone(timezone_str)

        markdown_contents = {}

        # Process entries and collect download tasks
        download_tasks = []
        processed_entries = []

        for entry in sorted(data, key=lambda x: x.get("created_at", "")):
            date_key, markdown_line, download_task = self._process_entry(
                entry, local_tz
            )
            if date_key and markdown_line:
                processed_entries.append((date_key, markdown_line))
                if download_task:
                    download_tasks.append(download_task)

        # Parallel processing for image downloads
        if download_tasks:
            self.logger.info(
                f"Starting parallel download of {len(download_tasks)} frames..."
            )
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all download tasks
                future_to_task = {
                    executor.submit(self._download_frame, download_url, file_path): (
                        download_url,
                        file_path,
                    )
                    for download_url, file_path in download_tasks
                }

                # Process completed downloads
                for future in as_completed(future_to_task):
                    download_url, file_path = future_to_task[future]
                    try:
                        success = future.result()
                        if not success:
                            self.logger.warning(
                                f"Failed to download frame: {file_path}"
                            )
                    except Exception as e:
                        self.logger.error(
                            f"Exception during frame download {file_path}: {e}"
                        )

        # Build markdown contents from processed entries
        for date_key, markdown_line in processed_entries:
            if date_key not in markdown_contents:
                markdown_contents[date_key] = ""
            markdown_contents[date_key] += markdown_line

        return markdown_contents

    def save_to_file(self, content, target_date):
        filepath = self.output_dir / f"{target_date}.md"
        try:
            filepath.write_text(content, encoding="utf-8")
            print(f"📝 Saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save file: {e}")
            return None
