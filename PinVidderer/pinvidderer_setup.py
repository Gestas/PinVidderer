import logging
import subprocess

from . import get_abs_path
from .utils import Utils, INIConfiguration

utils = Utils

logger = logging.getLogger(__name__)


class Setup:
    def __init__(self, config_dir, config_file):
        self.config_template = get_abs_path("errata/config.ini")
        self.systemd_template = get_abs_path("errata/pinvidderer.service")
        self.config_dir = utils.expand_path(config_dir)
        self.config_path = config_dir.joinpath(config_file)

    def create_config_file(self):
        self.config_dir.mkdir(exist_ok=True)
        self.config_path.write_bytes(self.config_template.read_bytes())

    def setup(self):
        self.create_config_file()
        ini = INIConfiguration(config_path=self.config_path, normalize=True)
        config = ini.get()
        print(
            f"A sample configuration file has been copied to {str(self.config_path)}\n"
        )
        print(
            f'Current Download Path: {str(config.get("pinvidderer", {}).get("download_path"))}'
        )
        print(
            f'Pinboard Tag To Use: {str(config.get("pinvidderer", {}).get("source_tag"))}'
        )
        print(
            f'Remove Tag After Download: {str(config.get("pinvidderer", {}).get("remove_tag"))}'
        )
        print(
            f'Delete Bookmark after Download: {str(config.get("pinvidderer", {}).get("delete_bookmark"))}'
        )
        print(
            f"The Pinboard API token (https://pinboard.in/settings/password) "
            f"can be added to the config file or exported as an environment variable."
        )
        print(f' $ export "PINBOARD_TOKEN"="<your:token>"')
        print(
            f"\nUpdate the sample configuration file and run `$ PinVidderer start` to start.\n"
        )
        utils.exiter(0)

    def create_systemd_service(self):
        pass
        # See https://weblog.christoph-egger.org/Installing_a_python_systemd_service_.html

    @staticmethod
    def get_systemd_unit_path() -> str:
        """Get the local systemd unit path
        :return: systemd unit path
        :rtype: str
        """
        failback = "/lib/systemd/system"
        try:
            command = ["pkg-config", "--variable=systemdsystemunitdir", "systemd"]
            path = subprocess.check_output(command, stderr=subprocess.STDOUT)
            return path.decode().replace('\n', '')
        except (subprocess.CalledProcessError, OSError):
            logger.warning(f'Unable to programmatically determine systemd service path. Failing to "{failback}".')
            return failback