"""Manage the PinVidderer history."""
import json
import logging
from datetime import datetime

from .utils import DateTimeFormatter, Utils

utils = Utils
dtf = DateTimeFormatter

logger = logging.getLogger(__name__)


class History:
    """The PinVidderer history."""

    def __init__(self, history_path):
        self.history_path = utils.expand_path(history_path)
        self.history_path.touch(exist_ok=True)

    def add(self, **kwargs: dict):
        """Add an event to the PinVidderer history.

        :param kwargs: Event details
        :type kwargs: dict
        """
        _event = {
            "dateTime": str(datetime.now(tz=None)),
            "videoFile": str(kwargs.get("videofile", "")),
            "url": kwargs["url"],
            "description": kwargs["description"],
            "downloadCompleted": kwargs["download_completed"],
            "error": kwargs.get("error", ""),
        }
        if "stats" in kwargs:
            _event.update(kwargs["stats"])
        self._add(_event)

    def get_event(self, url: str):
        """Return a specific event from the PinVidderer history.

        :param url: url to search for
        """
        _history = self.get()
        return next((_e for _e in _history if _e["url"] == url), None)

    def get(self) -> list:
        """Get the entire PinVidderer history.

        :return: A list of events
        :rtype: list
        """
        try:
            with open(self.history_path, "r") as file:
                history = json.load(file)
        except json.JSONDecodeError:  # If file is empty or corrupted.
            return []
        return history

    def _add(self, event: dict):
        """Persist a new event to disk.

        :param event: An event
        :type event: dict
        """
        _event = event
        logger.debug(f"  Adding event to history: {json.dumps(_event)}")
        _new_history = [_e for _e in self.get() if _e["url"] != _event["url"]]
        _new_history.append(_event)
        with open(self.history_path, "w") as file:
            json.dump(_new_history, file, indent=2)

    def remove(self, url: str, all_: bool):
        """Remove an event from the PinVidderer history.

        :param url: The URL of the event to remove
        :type url: str
        :param all_: Delete the entire history
        :param all_: bool
        """
        history = self.get()
        original_length = len(history)
        if all_:
            new_history = []
        else:
            new_history = [_e for _e in history if _e["url"] != url]
        new_length = len(new_history)
        with open(self.history_path, "w") as file:
            json.dump(new_history, file, indent=2)
        if original_length > new_length:
            logger.info(f"Removed {url} from history.")
            utils.exiter(0)
        else:
            if url:
                logger.error(f"{url} not found in history.")
                utils.exiter(1)
            utils.exiter(0)

    def print(self, human, failed):
        """Print the PinVidderer history.

        :param human: Format for humans
        :type human: bool
        :param failed: Only display failed downloads
        :type failed: bool
        """
        history = self.get()
        if failed:
            history = [d for d in history if d["downloadCompleted"] is False]
        if human:
            if not history:
                print("The history is empty.")
            for _event in history:
                _dt = dtf(dt=_event["dateTime"])
                print(f'\nTitle: {_event["description"]}')
                print(f"  Date: {_dt.world_24}")
                print(f'  URL: {_event["url"]}')
                if _event["downloadCompleted"]:
                    print("  Result: Success")
                    print(f'  Size: {_event["sizeStr"]}')
                    print(f'  Took: {_event["elapsedStr"]}')
                    print(f'  Download rate: {_event["rateStr"]}')
                    print(f'  Video: {_event["videoFile"]}')
                else:
                    print("  Result: Failed")
                    print(f'  Error: {_event["error"]}')
        else:
            print(json.dumps(history, sort_keys=True, indent=2))
