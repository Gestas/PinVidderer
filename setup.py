import os

from setuptools import setup


def read(readmefile):
    return open(os.path.join(os.path.dirname(__file__), readmefile)).read()


setup(
    name="PinVidderer",
    version=".01",
    author="Craig Carl",
    author_email="pinvidderer@gestas.net",
    description="A Bookmarked Video Downloader",
    license="MIT",
    keywords="Pinboard Youtube-dl Videos Youtube",
    url="https://github.com/Gestas/PinVidderer",
    packages=["PinVidderer"],
    include_package_data=True,
    package_data={"PinVidderer": ["errata/*"]},
    long_description=read("README.md"),
    python_requires=">=3.8",
    install_requires=[
        "Click",
        "setuptools~=54.0.0",
        "lxml~=4.6.2",
        "Pillow~=8.1.0",
        "youtube-dl~=2021.2.10",
        "rfc3339~=6.2",
        "iso8601~=0.1.14",
        "python-dateutil~=2.8.1",
        "requests~=2.25.1",
        "katna~=0.8.1",
        "opencv-contrib-python-headless~=4.5.1.48",
    ],
    entry_points={
        "console_scripts": [
            "PinVidderer=PinVidderer.PinVidderer:cli",
        ],
    },
)
