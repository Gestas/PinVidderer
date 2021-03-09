"""Download the video and thumbnail."""
from __future__ import unicode_literals

import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Union

import youtube_dl

from .custom_exceptions import CouldNotFindPathToVideo
from .images import Images
from .nfo import NFO
from .utils import PathDetails, Utils

pd = PathDetails
utils = Utils()

logger = logging.getLogger(__name__)


class YouTubeDLer:
    def __init__(self, configuration):
        self.statuses = []
        self.configuration = configuration
        self.download_dir = self.configuration.get("pinvidderer", {}).get(
            "download_path"
        )
        self.tmp_download_dir = None
        self.video_dir = None

    def get_video(self, url):
        """Prepare request for video.
        :param url: URL to the video to download
        :type url: str
        :return: Path to the video, download performance statistics
        :rtype: Path, dict
        """
        self.statuses = []
        options = self._get_ydl_options()
        # Create a tmp directory to work in.
        with tempfile.TemporaryDirectory(
            prefix=f"{str(self.download_dir)}/"
        ) as self.tmp_download_dir:
            self.tmp_download_dir = Path(self.tmp_download_dir)
            ytd_filename_format = "%(title)s.%(ext)s"
            tmp_output_path = f"{self.tmp_download_dir}/{ytd_filename_format}"
            options["outtmpl"] = tmp_output_path  # Tell youtube-dl to use the temp dir
            try:
                with youtube_dl.YoutubeDL(options) as _ydl:
                    video_metadata = _ydl.extract_info(url)
            except youtube_dl.utils.YoutubeDLError as err:
                _err = str(err).strip()
                logger.error(f'YoutubeDLError: {_err.removeprefix("ERROR:")}')
                raise err
            except Exception as err:
                raise err
            tmp_video_file_path = self._get_video_filepath()
            if not tmp_video_file_path:
                raise CouldNotFindPathToVideo(f'Video: {video_metadata["title"]}')
            stats = self._build_download_stats()
            if self.configuration.get("nfo", {}).get("create"):
                nfo = NFO(configuration=self.configuration)
                nfo.create(video_metadata, tmp_video_file_path)
            if self.configuration.get("pinvidderer", {}).get("get_fanart"):
                images = Images(configuration=self.configuration)
                images.process(working_path=self.tmp_download_dir)
            # Copy the files from the temp dir
            self.video_dir = Path(self.video_dir)
            self.video_dir = Path(self.download_dir.joinpath(self.video_dir))
            self.video_dir.mkdir(exist_ok=True)
            for file in self.tmp_download_dir.iterdir():
                new_path = self.video_dir.joinpath(file.name)
                logger.debug(f"Moving {file.name} to {self.video_dir}")
                new_path.write_bytes(file.read_bytes())
            video_file_path = self.video_dir.joinpath(tmp_video_file_path.name)
            # Occasionally ?something? is keeping a file open and we crash when the tempfile context
            # manager can't remove the temp dir. This sleep ?seems? to mitigate that.
            time.sleep(5)
        return video_file_path, stats

    def _get_video_filepath(self) -> Union[bool, Path]:
        """Attempt to find the video on disk.
        :return: Path to the video
        :rtype: Path
        """
        # YoutubeDL never returns the actual final filename, we only get temporary filenames.
        logger.debug(f"Files in temp dir:")
        for _f in self.tmp_download_dir.iterdir():
            logger.debug(f"  {_f}")
        video_file_name = None
        video_containers = [".mp4", ".mkv", ".avi", ".webm"]
        status = self.statuses[0]
        temp_file_name = Path(status["filename"])
        temp_file_name_stem = Path(
            temp_file_name.stem
        ).stem  # Strip Youtube-dls temporary name suffixes
        self.video_dir = temp_file_name_stem
        logger.debug(f'Temporary filename stem: "{temp_file_name_stem}"')
        while video_containers:
            container = video_containers.pop()
            looking_for = (
                f"{self.tmp_download_dir.joinpath(temp_file_name_stem)}{container}"
            )
            logger.debug(f"Looking for video: {looking_for}")
            if Path(looking_for).exists():
                video_file_name = looking_for
                logger.debug(f"Found video: {video_file_name}")
                break
        if not video_file_name:
            return False
        return self.tmp_download_dir.joinpath(video_file_name)

    def _build_download_stats(self):
        """Aggregate performance statistics about the download.
        :return: The stats
        :rtype: dict
        """
        size_bytes = 0
        rate_bytes = 0
        elapsed_float = 0
        for status in self.statuses:
            elapsed_float += status["elapsed"]
            size_bytes += status["downloaded_bytes"]
        if elapsed_float and size_bytes:
            rate_bytes = size_bytes / elapsed_float
        elapsed_str = f"{elapsed_float:.2f} seconds"
        size_str = utils.format_bytes(size_bytes)
        rate_str = f"{utils.format_bytes(rate_bytes)}/sec"
        return {
            "elapsedFloat": elapsed_float,
            "sizeBytes": size_bytes,
            "elapsedStr": elapsed_str,
            "sizeStr": size_str,
            "rateStr": rate_str,
        }

    def _get_ydl_options(self):
        """Set youtube-dl options."""
        options = {"format": self.configuration.get("youtubedl", {}).get("format")}
        options.update(
            {
                "quiet": True,
                "no_color": True,
                "no_warnings": True,
                "call_home": "False",
            }
        )
        if self.configuration.get("pinvidderer", {}).get("get_fanart"):
            options["writethumbnail"] = "True"
        logger.debug(f"Youtube-dl options: {json.dumps(options)}")
        options["progress_hooks"] = [self._ydl_hook]
        options["logger"] = YTDLogger()
        return options

    def _ydl_hook(self, status):
        # logger.debug(status)  # Very verbose
        if status["status"] == "finished":
            logger.debug(f"HOOK: {status}")
            self.statuses.append(status)


class YTDLogger:
    """A custom logger is the easiest way to wrangle youtube-dl's schizophrenic output."""

    def debug(self, message):
        response = f"YTDLogger DEBUG: {message}"
        return response

    def error(self, message):
        response = f"YTDLogger ERROR: {message}"
        return response

    def warning(self, message):
        response = f"YTDLogger WARNING: {message}"
        return response

    def info(self, message):
        response = f"YTDLogger INFO: {message}"
        return response

    def critical(self, message):
        response = f"YTDLogger CRITICAL: {message}"
        return response
