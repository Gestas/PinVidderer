"""PinVidderer Custom Exceptions."""


class VideoFileExists(Exception):
    """Exception raised if video is already on disk."""

    def __init__(self, path=None, url=None, message="Video file is already on disk."):
        self._url = url
        self._path = path
        self._message = message
        super().__init__(self._message)

    def __str__(self):
        if self._path:
            return f"{self._path} -> {self._message}"
        if self._url:
            return f"{self._path} -> {self._message}"


class UnsupportedURL(Exception):
    """If youtube-dl doesn't support the URL."""

    def __init__(self, message="youtube-dl doesn't support this URL."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class CouldNotFindPathToVideo(Exception):
    """If we could not determine the path to the video."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"
