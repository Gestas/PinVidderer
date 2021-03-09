"""Parse user and configuration file input and start."""
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from .history import History
from .pinboard import Pinboard
from .utils import DateTimeFormatter, INIConfiguration, Utils
from .video import Video

utils = Utils
dtf = DateTimeFormatter

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, loglevel):
        """Load the config and run."""
        config_file = "config.ini"
        config_dir = Path(utils.expand_path("~/.pinvidderer"))
        self.configuration = self.get_config(
            config_dir=config_dir, config_file=config_file
        )
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
        mock_bookmark = {"href": url, "description": "None (run once)"}
        video = Video(configuration=self.configuration)
        video.preflight(mock_bookmark)

    def status(self):
        pass

    def get_history(self, human, failed):
        self.history.print(human, failed)

    def remove_from_history(self, url, all_):
        self.history.remove(url, all_)

    def watcher(self):
        """Start watching Pinboard.in."""
        pinboard = Pinboard(configuration=self.configuration)
        video = Video(configuration=self.configuration)
        logger.debug("-- STARTING WATCHER LOOP --")
        pb_last_checked = 0
        poll_interval = self.configuration.get("pinvidderer", {}).get("poll_interval")
        while True:
            bookmarks = []
            pb_last_updated = pinboard.get_last_updated()
            if pb_last_updated < pb_last_checked:
                logger.debug(
                    f"Pinboard has not been updated since {dtf(pb_last_checked).world_24}. Nothing to do."
                )
                logger.debug(
                    f"Pinboard last updated: {dtf(pb_last_updated).world_24}. Last checked: "
                    f"{dtf(pb_last_checked).world_24}"
                )
            else:
                pb_last_checked = time.time()
                bookmarks = pinboard.get_bookmarks(
                    self.configuration.get("pinvidderer", {}).get("source_tag")
                )
                logger.debug(f"    Got {len(bookmarks)} bookmark(s) ->")
                for bookmark in bookmarks:
                    logger.debug(f'    * {bookmark["description"]}')
            while bookmarks:
                bookmark = bookmarks.pop()
                video.preflight(bookmark)
            logger.debug(
                f" Sleeping until {datetime.now(tz=None) + timedelta(seconds=int(poll_interval))}"
            )
            time.sleep(int(poll_interval))

    @staticmethod
    def get_config(config_dir, config_file):
        """Get the user configuration from disk and environment.
        :param config_dir: Path to the configuration directory
        :type config_dir: Path
        :param config_file: Name of the configuration file
        :type config_file:
        :return: str
        :rtype: dict
        """
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir.joinpath(config_file)
        if not config_path.exists():
            config_template = Path("./errata/config.ini").expanduser()
            config_path.write_bytes(config_template.read_bytes())
        ini = INIConfiguration(config_path=config_path, normalize=True)
        config = ini.get()
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
        download_path = config.get("pinvidderer", {}).get("download_path")
        download_path = utils.expand_path(download_path)
        config["pinvidderer"]["download_path"] = download_path
        return config

    @staticmethod
    def _setup_logging(loglevel):
        """Setup the logger.
        :param loglevel: Level for the logger
        :type loglevel: str
        """

        logger = logging.getLogger()
        logger.setLevel(loglevel)
        formatter = logging.Formatter("{levelname}: {message}", style="{")
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
