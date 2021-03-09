"""Thumbnail and poster images."""
import logging
from pathlib import Path

from PinVidderer.utils import Utils

logger = logging.getLogger(__name__)
utils = Utils


class Images:
    def __init__(self, configuration):
        self.configuration = configuration
        self.working_path = None
        self.fanart_filename = self.configuration.get("pinvidderer", {}).get(
            "fanart_filename", "fanart"
        )
        self.fanart_format = self.configuration.get("pinvidderer", {}).get(
            "fanart_format", "jpeg"
        )
        self.poster_filename = self.configuration.get("pinvidderer", {}).get(
            "poster_filename", "poster"
        )
        self.poster_format = self.configuration.get("pinvidderer", {}).get(
            "poster_format", "jpeg"
        )
        self.poster_aspect_ratio = self.configuration.get("pinvidderer", {}).get(
            "poster_aspect_ratio", "2:3"
        )

    def process(self, working_path):
        self.working_path = Path(working_path)
        self._rename()
        self._convert_fanart()
        if self.configuration.get("pinvidderer", {}).get("create_poster"):
            self._poster()

    def _rename(self):
        image_formats = ["jpeg", "jpg", "png", "webp"]
        for _f in image_formats:
            images = list(self.working_path.glob(f"*.{_f}"))
            if images:
                image_path = Path(images[0])
                new_name = image_path.rename(
                    f"{self.working_path}/{self.fanart_filename}.{_f}"
                )
                logger.debug(f"Renamed {image_path} to {new_name}.")
                return True

    def _convert_fanart(self):
        """Convert fanart images to <fanart format>"""
        fanart = list(self.working_path.glob(f"{self.fanart_filename}*"))
        if len(fanart) > 1:
            logger.warning(
                f"There should only have been 1 image file present. Found {len(fanart)}, {fanart}."
            )
        for file in fanart:
            logger.debug(f"Converting {file} to {self.fanart_format}")
            utils.image_format_converter(
                source_path=file, delete_original=True, target_format=self.fanart_format
            )

    def _poster(self):
        """Create a poster sized crop of the thumbnail"""
        import cv2
        from Katna.image import Image

        img = Image()

        def _do_crop(_filter):
            _crop = img.crop_image_with_aspect(
                file_path=fanart_file,
                crop_aspect_ratio=self.poster_aspect_ratio,
                num_of_crops=1,
                filters=_filter,
                down_sample_factor=4,
            )
            return _crop

        fanart_file = f"{self.working_path}/{self.fanart_filename}.{self.fanart_format}"
        logger.debug(f"Creating a poster from {fanart_file}.")
        crop = _do_crop(["text"])
        if len(crop) == 0:
            logger.debug(
                "Unable to find a good crop with the text filter. Cropping without a filter."
            )
            crop = _do_crop([])
        poster = cv2.imread(fanart_file)
        logger.debug(f'WORKING PATH: {str(str(self.working_path) + "/")}')
        logger.debug(f"POSTER FILENAME: {self.poster_filename}")
        logger.debug(f"POSTER FORMAT: {self.poster_format}")
        img.save_crop_to_disk(
            crop[0],
            poster,
            file_path=str(str(self.working_path) + "/"),
            file_name=self.poster_filename,
            file_ext=f".{self.poster_format}",
        )
        return True
