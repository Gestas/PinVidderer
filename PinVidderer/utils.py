"""A generally generic set of utilities."""
import configparser
import logging
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Union

import iso8601
import rfc3339
from dateutil import tz

logger = logging.getLogger(__name__)


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def expand_path(path: Union[Path, str]) -> Path:
        """User and variable expansion for paths.

        :param path: A Path or path-like string
        :type path: [Path, str]
        :return: A path
        :rtype: Path
        """
        return Path(os.path.expandvars(Path(path).expanduser()))

    @staticmethod
    def format_bytes(bytes_: int) -> str:
        """Format bytes into a pretty string.

        :param bytes_: bytes
        :type bytes_: int
        :return: A pretty string
        :rtype: str
        """
        if bytes_ is None:
            return "N/A"
        if isinstance(bytes_, str):
            _bytes = float(bytes_)
        exponent = 0 if bytes_ == 0.0 else int(math.log(bytes_, 1024.0))
        suffix = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"][exponent]
        converted = float(bytes_) / float(1024 ** exponent)
        return f"{converted:.2f}{suffix}"

    @staticmethod
    def exiter(level, message=None):
        """Cleanup and exit the application.

        :param level: Exit code
        :type level: int
        :param message: Exit message
        :type message: str
        """
        if level != 0 and message:
            logger.error(f"{message}")
        elif message:
            logger.debug(f"{message}")
        sys.exit(level)

    @staticmethod
    def image_format_converter(
        source_path: [str, Path],
        target_format: [str],
        destination_path=None,
        delete_original=False,
    ):
        """Creates a new image of the requested format. Optionally deletes the original.

        :param source_path: Source file
        :param target_format: Target format. Must be supported by Pillow.
        :param destination_path: Optional destination path.
        :param delete_original: Delete the original if conversion succeeds.
        """
        from PIL import Image

        if not destination_path:
            _destination_path = source_path.with_suffix("." + target_format)
        else:
            _destination_path = Path(destination_path).expanduser()
        try:
            _file = open(_destination_path, "w")
        except OSError as e:
            logger.error(
                f"Unable to create thumbnail file {str(_destination_path)}, {str(e)}."
            )
            return
        try:
            _image = Image.open(source_path).convert("RGB")
            _image.save(_file, target_format)
        except Exception as e:
            raise e
        if delete_original:
            source_path.unlink()

    def signal_handler(self, sig, frame, **kwargs):
        """Catch signals.

        :param sig: A signal
        :type sig: Signal
        :param frame:
        :type frame:
        :param kwargs:
        :type kwargs:
        """
        self.exiter(1, message=f"SIGINT: {sig}", **kwargs)


class DateTimeFormatter:
    """One datetime formatter to rule them all."""

    def __init__(self):
        self._usa_format_12 = "%m/%d/%Y %I:%M:%S"
        self._usa_format_24 = "%m/%d/%Y %H:%M:%S"
        self._global_format_12 = "%d/%m/%Y %H:%M:%S"
        self._global_format_24 = "%d/%m/%Y %I:%M:%S"

    def global12(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._global_format_12)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._global_format_12)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._global_format_12)

    def global24(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._global_format_24)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._global_format_24)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._global_format_24)

    def usa12(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._usa_format_12)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._usa_format_12)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._usa_format_12)

    def usa24(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._usa_format_24)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._usa_format_24)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._usa_format_24)

    @staticmethod
    def r3339(dt=None):
        if not dt:
            return rfc3339.rfc3339(datetime.utcnow())
        try:
            return rfc3339.rfc3339(datetime.fromtimestamp(float(dt)))
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return rfc3339.rfc3339(_i)

    @staticmethod
    def i8601(dt=None):
        if not dt:
            return datetime.isoformat(datetime.utcnow())
        try:
            return datetime.isoformat(datetime.fromtimestamp(float(dt)))
        except (TypeError, ValueError):
            return iso8601.parse_date(str(dt))

    @staticmethod
    def epoch(dt=None):
        if not dt:
            return datetime.now().timestamp()
        try:
            return float(dt)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.timestamp()

    @staticmethod
    def utc_to_local(utc_dt: datetime):
        """Convert a UTC datetime to a local timezone aware datetime.

        :param utc_dt: Datetime using the UTC timezone
        :type utc_dt: datetime
        :return: Parameter datetime adjusted to use the local timezone
        :rtype: datetime
        """
        utc_dt = utc_dt.replace(tzinfo=tz.gettz("UTC"))
        return utc_dt.astimezone(tz.tzlocal())

    @staticmethod
    def local_to_utc(local_dt):
        """Convert a local datetime to a UTC timezone aware datetime.

        :param local_dt: Datetime using the local timezone
        :type local_dt: datetime
        :return: Parameter datetime adjusted to use the UTC timezone
        :rtype: datetime
        """
        local_dt = local_dt.replace(tzinfo=tz.tzlocal())
        return local_dt.astimezone(tz.tzlocal())

    @staticmethod
    def tz_to_tz(dt, source_tz, dest_tz):
        """Covert a datetime object from <timezone> to <timezone>.

        :param dt: A datetime
        :type dt: datetime
        :param source_tz: The timezone of the supplied datetime
        :type source_tz: str
        :param dest_tz: The timezone to convert to
        :type dest_tz: str
        :return: A datetime
        :rtype: datetime
        """
        dt = dt.replace(tzinfo=tz.gettz(source_tz))
        return dt.replace(tzinfo=tz.gettz(dest_tz))


class PathDetails:
    """One PathThingy to rule them all. Or: A single place to get lots of details about a path."""

    def __init__(self, path: [Path, str]):
        self.path = Path(path)

        self.file_name = None
        self.file_size = None
        self.path_type = None
        self.original_path = None
        self.file_extension = None
        self.full_path_to_directory = None
        self.file_name_without_extension = None
        self.full_path_to_parent_directory = None
        self.full_path_without_file_extension = None

        self.user_expanded_path = Path(self.path.expanduser())
        self.fully_expanded_path = Path(os.path.expandvars(self.user_expanded_path))
        self.all_path_parts = Path(self.fully_expanded_path).parts

        if self.fully_expanded_path.suffixes:
            self.file_name = self.fully_expanded_path.name
            self.file_extension = self.fully_expanded_path.suffix
            self.file_name_without_extension = Path(self.file_name).stem
            self.full_path_to_directory = Path(self.fully_expanded_path.parents[0])
            self.full_path_without_file_extension = (
                self.full_path_to_directory.joinpath(self.file_name_without_extension)
            )
        else:
            self.full_path_to_directory = self.fully_expanded_path
            self.file_extensions = None

        self.path_exists = self.fully_expanded_path.exists()
        if self.path_exists:
            if self.fully_expanded_path.is_dir():
                self.path_type = "dir"
            if self.fully_expanded_path.is_file():
                self.path_type = "file"
        self.file_size = self.fully_expanded_path.stat().st_size


class INIConfiguration:
    def __init__(self, config_path, normalize=False):
        """Get or update an INI formatted configuration.

        :param config_path: Path to a INI formatted file.
        :type config_path: [Path, str]
        :param normalize: Capitalized keys are lowercased and spaces in keys are replaced with '_'.
        :type normalize: bool
        """
        self.config = {}
        _config_dict = {}
        self._config_path = Utils.expand_path(config_path)
        self.update = None
        self.normalize = normalize

    def _format_keys(self, str_):
        if not self.normalize:
            return str_
        if self.update:
            str_ = str_.upper()
            return str_.replace("_", " ")
        str_ = str_.lower()
        return str_.replace(" ", "_")

    @staticmethod
    def _format_values(v):
        if v.lower() in ["1", "yes", "true", "on"]:
            return True
        if v.lower() in ["0", "no", "false", "off"]:
            return False
        return v

    def get(self):
        """Get and return the configuration from disk as a dict
        :return: The configuration as a dict
        :rtype: dict
        """
        _config_file = None
        _parsed_config = configparser.ConfigParser()
        try:
            _config_file = open(self._config_path, "r")
        except OSError as e:
            logger.error(str(e))
            Utils.exiter(1)
        try:
            _parsed_config.read_file(_config_file)
        except configparser.ParsingError as e:
            logger.error(str(e))
            Utils.exiter(1)

        _defaults = _parsed_config.defaults()
        _t = {}
        for (_k, _v) in _defaults:
            _t[self._format_keys(_k)] = self._format_values(_v)
        self.config[self._format_keys("defaults")] = _t

        for _s in _parsed_config.sections():
            _t = {}
            for (_k, _v) in _parsed_config.items(_s):
                _t[self._format_keys(_k)] = self._format_values(_v)
            self.config[self._format_keys(_s)] = _t
        return self.config
