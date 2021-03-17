"""Parse user and configuration file input and start."""
import logging
import os
import time
from datetime import datetime, timedelta
from logging import handlers
from pathlib import Path

from .history import History
from .pinboard import Pinboard
from .utils import DateTimeFormatter, INIConfiguration, Utils
from .video import Video
from .pinvidderer_setup import Setup

utils = Utils
dtf = DateTimeFormatter()

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, loglevel, is_setup=False):
        """Load the config and run."""
        self.created_config = False
        config_file = "config.ini"
        config_dir = Path(utils.expand_path("~/.pinvidderer"))
        config_path = config_dir.joinpath(config_file)
        if is_setup or not config_path.exists():
            pinvidderer_setup = Setup(config_dir=config_dir, config_file=config_file)
            pinvidderer_setup.setup()
        self.configuration = self.get_config(config_path=config_path)
        self.console_logger = loglevel
        loglevel = loglevel or self.configuration.get("dev", {})["log_level"]
        self._setup_logging(loglevel)
        self.pinboard = None
        history_path = config_dir.joinpath(
            self.configuration.get("dev", {})["history_file"]
        )
        self.history = History(history_path=history_path)

    def start(self):
        download_path = Path(
            self.configuration.get("pinvidderer", {}).get("download_path")
        )
        if not download_path.is_dir():
            utils.exiter(
                1, message=f'"Download directory does not exist: {download_path}'
            )
        self.watcher()

    def runonce(self, url):
        # Mock a bookmark and run
        mock_bookmark = {"href": url, "description": "Run Once"}
        video = Video(configuration=self.configuration)
        video.preflight(mock_bookmark)

    def status(self):
        utils.exiter(0, message="TODO")

    def get_history(self, human, failed):
        self.history.print(human, failed)

    def remove_from_history(self, url, all_):
        self.history.remove(url, all_)

    def watcher(self):
        """Start watching Pinboard.in."""
        pinboard = Pinboard(configuration=self.configuration)
        video = Video(configuration=self.configuration)
        logger.info("--------- STARTING WATCHER LOOP ---------")
        pb_last_checked = 0
        poll_interval = self.configuration.get("pinvidderer", {}).get("poll_interval")
        while True:
            bookmarks = []
            pb_last_updated = pinboard.get_last_updated()
            if pb_last_updated < pb_last_checked:
                logger.debug(
                    f"Pinboard has not been updated since {dtf.global24(pb_last_updated)}. Nothing to do."
                )
            else:
                pb_last_checked = time.time()
                bookmarks = pinboard.get_bookmarks(
                    self.configuration.get("pinvidderer", {}).get("source_tag")
                )
                logger.info(f"Got {len(bookmarks)} bookmark(s) ->")
                for bookmark in bookmarks:
                    logger.info(f'  * {bookmark["description"]}')
            while bookmarks:
                bookmark = bookmarks.pop()
                video.preflight(bookmark)
            logger.info(
                f"Sleeping until {datetime.now(tz=None) + timedelta(seconds=int(poll_interval))}"
            )
            time.sleep(int(poll_interval))

    def get_config(self, config_path):
        """Get the user configuration from disk and environment.
        :param config_path: Path to the configuration file
        :type config_path: Path, str
        :return: str
        :rtype: dict
        """
        ini = INIConfiguration(config_path=config_path, normalize=True)
        config = ini.get()
        download_path = config.get("pinvidderer", {}).get("download_path")
        download_path = utils.expand_path(download_path)
        config["pinvidderer"]["download_path"] = download_path
        token = config.get("auth", {}).get("pinboard_token") or os.getenv(
            "PINBOARD_TOKEN"
        )
        if not token:
            utils.exiter(
                1,
                message='ERROR: A Pinboard token is required. Specify it with a "PINBOARD_TOKEN" '
                "environment variable or in the config.ini file.",
            )
        config["auth"]["pinboard_token"] = token
        return config

    def _setup_logging(self, loglevel):
        """Setup the logger.
        :param loglevel: Level for the logger
        :type loglevel: str
        """
        logger = logging.getLogger()
        logger.setLevel(loglevel)

        logs_dir = Path(self.configuration.get("dev", {})["logs_dir"])
        logs_dir = logs_dir.expanduser()
        logs_dir.mkdir(exist_ok=True)

        log_path = logs_dir.joinpath(self.configuration.get("dev", {})["log_filename"])
        rollover_required = log_path.exists()
        log_retention = int(self.configuration.get("dev", {})["log_retention"])
        # file_formatter = logging.Formatter("{asctime}: {message}", style="{")
        file_formatter = logging.Formatter("{dtf.r3339}: {message}", style="{")
        file = logging.handlers.RotatingFileHandler(filename=log_path, backupCount=log_retention)
        file.setFormatter(file_formatter)
        logger.addHandler(file)
        if rollover_required:
            logger.critical(f'\n--------- Log closed {dtf.r3339} ---------')
            file.doRollover()
        logger.critical(f'--------- Log started {dtf.r3339} ---------')

        if self.console_logger:
            console_formatter = logging.Formatter("{levelname}: {message}", style="{")
            console = logging.StreamHandler()
            console.setFormatter(console_formatter)
            logger.addHandler(console)
