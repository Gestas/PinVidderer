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
from . import get_abs_path

utils = Utils
dtf = DateTimeFormatter

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, loglevel, is_setup=False):
        """Load the config and run."""
        self.is_setup = is_setup
        self.created_config_file = False
        config_file = "config.ini"
        config_dir = Path(utils.expand_path("~/.pinvidderer"))
        self.config_path = config_dir.joinpath(config_file)
        self.configuration = self.get_config(
            config_dir=config_dir, config_file=config_file
        )
        if self.created_config_file or is_setup:
            self.setup()
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

    def setup(self):
        print(
            f"A sample configuration file has been copied to {str(self.config_path)}\n"
        )
        print(
            f'Current Download Path: {str(self.configuration.get("pinvidderer", {}).get("download_path"))}'
        )
        print(
            f'Pinboard Tag To Use: {str(self.configuration.get("pinvidderer", {}).get("source_tag"))}'
        )
        print(
            f'Remove Tag After Download: {str(self.configuration.get("pinvidderer", {}).get("remove_tag"))}'
        )
        print(
            f'Delete Bookmark after Download: {str(self.configuration.get("pinvidderer", {}).get("delete_bookmark"))}'
        )
        print(
            f"The Pinboard API token (https://pinboard.in/settings/password) "
            f"can be added to the config file or exported as an environment variable."
        )
        print(f' $ export "PINBOARD_TOKEN"="<your:token>"')
        print(
            f"\nUpdate the sample configuration file and run `$ PinVidderer start` to start."
        )
        utils.exiter(0)

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

    def get_config(self, config_dir, config_file):
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
            config_template = "errata/config.ini"
            config_template = get_abs_path(config_template)
            config_path.write_bytes(config_template.read_bytes())
            self.created_config_file = True
        ini = INIConfiguration(config_path=config_path, normalize=True)
        config = ini.get()
        download_path = config.get("pinvidderer", {}).get("download_path")
        download_path = utils.expand_path(download_path)
        config["pinvidderer"]["download_path"] = download_path
        if self.created_config_file or self.is_setup:
            return config
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
