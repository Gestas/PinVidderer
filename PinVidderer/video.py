"""Videos."""
import logging
from pathlib import Path, PurePath

import youtube_dl

from PinVidderer.custom_exceptions import VideoFileExists
from PinVidderer.history import History
from PinVidderer.pinboard import Pinboard
from PinVidderer.utils import DateTimeFormatter, PathDetails, Utils
from PinVidderer.youtubedler import YouTubeDLer

logger = logging.getLogger(__name__)
utils = Utils
dtf = DateTimeFormatter


class Video:
    def __init__(self, configuration):
        self.configuration = configuration
        self.pinboard = Pinboard(configuration=self.configuration)
        config_path = self.configuration.get("dev", {}).get("config_dir")
        history_path = Path(config_path).joinpath(
            self.configuration.get("dev", {}).get("history_file")
        )
        self.download_path = Path(
            self.configuration.get("pinvidderer", {}).get("download_path")
        )
        self.backup_file_suffix = self.configuration.get("pinvidderer", {}).get(
            "backup_file_suffix"
        )
        self.history = History(history_path=history_path)
        self.youtubedler = YouTubeDLer(configuration=self.configuration)

    def preflight(self, bookmark):
        """Run pre-flight checks, get the video, update the history.
        :param bookmark: Pinboard.in bookmark
        :type bookmark: dict
        :return: Status
        :rtype: bool
        """
        backups = []
        force = self.configuration.get("pinvidderer", {}).get("force")
        logger.debug(f'---------- Downloading {bookmark["description"]}  ----------')
        historical_event = self.history.get_event(bookmark["href"])
        if not force and historical_event:
            logger.warning(f"-- Bookmark is in the history, skipping.")
            return
        if force and historical_event:
            backups = self.backup(historical_event["videoFile"])
        try:
            video_path, stats = self.youtubedler.get_video(bookmark["href"])
            self.history.add(
                stats=stats,
                url=bookmark["href"],
                videofile=video_path,
                description=bookmark["description"],
                download_completed=True,
                error="none",
            )
            self.pinboard.update_bookmarks(bookmark)
            self.delete_backups(backups=backups)
            return True
        except VideoFileExists:
            logger.warning(
                f'Video {historical_event["videoFile"]} is on disk but not in the history. Adding a stub to history.'
            )
            self.history.add(
                url=bookmark["href"],
                videofile=historical_event["videoFile"],
                description=bookmark["description"],
                download_completed=True,
                error="Video file was found on disk but not in the history.",
            )
            self.pinboard.update_bookmarks(bookmark)

        except youtube_dl.utils.YoutubeDLError as err:
            self.history.add(
                url=bookmark["href"],
                description=bookmark["description"],
                download_completed=False,
                error=err,
            )
            self.restore_backups(backups=backups)
            return True

    def backup(self, video_file_path) -> list:
        """Backup files before attempting to overwrite.
        :param video_file_path: Path to a video
        :type video_file_path: Path
        :return backups: List of backups
        :rtype backups: list
        """
        backups = []
        print(f"BACKUP video_file_path: {video_file_path}")
        video_file_stem = PurePath(video_file_path).stem
        print(f"BACKUP video_file_stem: {video_file_stem}")
        search_str = f"{video_file_stem}*"
        print(f"BACKUP  search_str: { search_str}")
        files = list(self.download_path.glob(search_str))
        print(f"BACKUP  files: { files}")
        for file in files:
            backup_name = file.rename(f"{file}{self.backup_file_suffix}")
            backups.append(backup_name)
            logger.debug(f'Backed up "{file}" to "{backup_name}"')
        print(f"BACKUPs: {files}")
        return backups

    @staticmethod
    def delete_backups(backups):
        """Delete any backed up files.

        :param backups: List of backups
        :type backups: list
        """
        for backup in backups:
            if Path(backup).is_dir():
                for f in Path(backup).iterdir():
                    f.unlink()
                    logger.debug(f'Deleted backup file "{f}".')
                Path(backup).rmdir()
                logger.debug(f'Deleted backup directory "{backup}".')
            else:
                Path(backup).unlink()
                logger.debug(f'Deleted backup "{backup}".')

    @staticmethod
    def restore_backups(backups):
        """Restore any backed up files.

        :param backups: List of backups
        :type backups: list
        """
        for backup in backups:
            pd = PathDetails(path=backup)
            new_name = backup.rename(pd.full_path_without_file_extension)
            logger.debug(f'Restored "{backup}" to "{new_name}".')
