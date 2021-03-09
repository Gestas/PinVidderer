"""NFO file utilities."""
import logging
import re
# Thanks to JGoutin @ https://github.com/JGoutin/movie_nfo_generator/blob/master/movie_nfo_generator/nfo.py
from pathlib import Path

from lxml.etree import Element, ElementTree, ParseError, SubElement

from .utils import PathDetails

logger = logging.getLogger(__name__)
pd = PathDetails


class NFO:
    """A NFO file."""

    def __init__(self, configuration):
        self.configuration = configuration
        self.video_metadata = None
        self.nfo_details = None
        self.video_path = None

    def create(self, video_metadata, video_path):
        """Builds the NFO content.

        :param video_metadata: Video metadata
        :type video_metadata: dict
        :param video_path: Path to the video file
        :type video_path: Path
        """
        source_str = ""
        self.video_metadata = video_metadata
        self.video_path = video_path
        plot = self.video_metadata.get("description")
        plot_prefix = self.configuration.get("nfo", {}).get("plot_prefix")
        newline_delimiter = self.configuration.get("nfo", {}).get("newline_delimiter")
        plot_suffix = self.configuration.get("nfo", {}).get("plot_suffix")
        webpage_url = self.video_metadata.get("webpage_url")
        hyperlink_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        if webpage_url:
            source_str = f'Source URL - <a href="{webpage_url}">{webpage_url}</a>'
        if plot:
            urls = re.findall(hyperlink_regex, plot)
            for url in urls:
                replacement = f'<a href="{url[0]}">{url[0]}</a>'
                plot = plot.replace(url[0], replacement)
            if plot_prefix:
                plot = f"{plot_prefix}{plot}"
            if newline_delimiter:
                plot = plot.replace("\n", newline_delimiter)
            plot = f"{plot}{newline_delimiter}{newline_delimiter}{source_str}"
            if plot_suffix:
                plot = f"{plot}{plot_suffix}"
        else:
            plot = source_str

        self.nfo_details = {
            "title": self.video_metadata.get("title", "N/A"),
            "plot": plot,
            "genre": self.video_metadata.get("categories", []),
            "userrating": self.video_metadata.get("average_rating", 0),
            "studio": self.video_metadata.get("uploader_url", "N/A"),
        }
        if premiered := self.video_metadata.get(
            "upload_date"
        ):  # Formatted as "20200302"
            premiered = premiered[:4] + "-" + premiered[4:]
            premiered = premiered[:7] + "-" + premiered[7:]
            self.nfo_details["premiered"] = premiered  # Formatted as "2020-03-02"
        if runtime := self.video_metadata.get("duration"):  # Seconds (float)
            runtime = runtime / 60
            runtime = f"{runtime:.2f}"
            self.nfo_details["runtime"] = runtime  # Minutes
        self._write_nfo(nfo_details=self.nfo_details)

    def _write_nfo(self, nfo_details):
        """Write the NFO document to disk.

        :param nfo_details: The NFO contents
        :type nfo_details: ElementTree
        """
        nfo_root = Element("movie")

        for field_name, values in nfo_details.items():
            if not values:
                continue
            if not isinstance(values, list):
                values = [values]
            for value in values:
                SubElement(nfo_root, field_name).text = f"{value}"

        nfo_file = Path(self.video_path).with_suffix(".nfo")
        logger.debug(f"Creating NFO file @ {nfo_file}")
        # logger.debug(f"NFO details: {json.dumps(self._nfo_details)}")

        try:
            ElementTree(nfo_root).write(
                str(nfo_file),
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True,
            )
        except ParseError as err:
            logger.warning(f"Could not parse the XML in the NFO, {str(err)}.")
