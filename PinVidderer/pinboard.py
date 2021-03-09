"""Manage Pinboard.in."""
import logging

from PinVidderer.do_http import DoHTTP

from .utils import DateTimeFormatter

logger = logging.getLogger(__name__)


class Pinboard:
    def __init__(self, configuration):
        self.configuration = configuration
        self.token = self.configuration.get("auth", {}).get("pinboard_token")
        self.endpoint = "https://api.pinboard.in"
        self.do_http = DoHTTP(method="GET", endpoint=self.endpoint, token=self.token)

    def get_bookmarks(self, tag):
        """Get bookmarks from Pinboard.

        :param tag: Tag to search for
        :type tag: str
        :return: Bookmarks
        :rtype: dict
        """
        _path = "/v1/posts/all"
        _params = {"format": "json", "tag": tag}
        _response = self.do_http.request(path=_path, params=_params, do_raise=False)
        if _response.status_code == 200:
            return _response.json()
        logger.error(
            f"  Error getting get_bookmarks: {_response.text}, {_response.status_code}."
        )
        return False

    def update_bookmarks(self, bookmark):
        """Update bookmarks
        :param bookmark: A bookmark
        :type bookmark: dict
        """
        if "tags" not in bookmark:
            logger.debug("Using a mocked bookmark, to tags to manage.")
            return True
        tag = self.configuration.get("pinvidderer", {}).get("source_tag")
        remove_tag = self.configuration.get("pinvidderer", {}).get("remove_tag")
        delete_bookmark = self.configuration.get("pinvidderer", {}).get(
            "delete_bookmark"
        )
        if delete_bookmark:
            if not self.delete_bookmark(bookmark):
                self.remove_tag(bookmark, tag)
        elif remove_tag:
            self.remove_tag(bookmark, tag)
        return True

    def delete_bookmark(self, bookmark):
        """Delete a bookmark.

        :param bookmark: A Pinboard bookmark object.
        :type bookmark: dict
        """
        tags = bookmark["tags"].split(" ")
        if len(tags) > 1:
            logger.debug(
                f'Not deleting {bookmark["description"]} because it has more than 1 tag. ({len(tags)})'
            )
            return False
        logger.debug(f'  Deleting bookmark "{bookmark["description"]}"')
        _path = "/v1/posts/delete"
        _params = {"format": "json", "url": bookmark["href"]}
        _response = self.do_http.request(path=_path, params=_params, do_raise=False)
        if _response.status_code == 200:
            return True
        logger.error(
            f"  Error deleting bookmark: {_response.text}, {_response.status_code}."
        )
        return True

    def remove_tag(self, bookmark, tag):
        """Remove a tag from a Pinboard bookmark.

        :param bookmark: A Pinboard bookmark object
        :type bookmark: dict
        :param tag: A Pinboard tag
        :type tag: str
        """
        logger.debug(f'  Removing the "{tag}" tag.')
        _path = "/v1/posts/add"
        _replacement_bookmark = {
            "replace": "yes",
            "url": bookmark["href"],
            "description": bookmark["description"],
            "time": bookmark["time"],
            "shared": bookmark["shared"],
            "toread": bookmark["toread"],
        }
        _existing_tags = bookmark["tags"]
        _new_tags = _existing_tags.replace(tag, "")
        if _new_tags:
            _replacement_bookmark["tags"] = _new_tags
        _response = self.do_http.request(
            path=_path, params=_replacement_bookmark, do_raise=False
        )
        if _response.status_code == 200:
            return True
        logger.error(
            f"  Error removing tag: {_response.text}, {_response.status_code}."
        )
        return False

    def get_last_updated(self) -> int:
        """Returns the most recent time a bookmark was added, updated or deleted.

        :return: The most recent time a bookmark was added, updated or deleted as epoch.
        :rtype: float
        """
        _path = "/v1/posts/update"
        _params = {"format": "json"}
        _response = self.do_http.request(path=_path, params=_params, do_raise=False)
        _json = _response.json()
        _dtf = DateTimeFormatter(dt=_json["update_time"])
        return _dtf.epoch
