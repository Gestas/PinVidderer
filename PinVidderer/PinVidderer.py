#!/usr/bin/env python
import signal

import click

from .client import Client
from .utils import Utils

utils = Utils()
signal.signal(signal.SIGINT, utils.signal_handler)


class Config(object):
    def __init__(self):
        self.loglevel = None


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option(
    "--loglevel",
    default=None,
    type=click.Choice(["ERROR", "WARNING", "INFO", "DEBUG", "CRITICAL"]),
    help="Sets the logging level, overriding the value in config.ini. If a loglevel is set here messages will be sent "
         "to the console as well as the log file.",
)
@pass_config
def cli(config, loglevel):
    """A Bookmarked Video Downloader."""
    # signal.signal(signal.SIGINT, utils.signal_handler)
    config.loglevel = loglevel


@cli.command(help="Setup PinVidderer.")
@pass_config
def setup(config):
    """Setup PinVidderer."""
    config.client = Client(loglevel=config.loglevel, is_setup=True)


@cli.command(help="Start watching Pinboard.")
@pass_config
def start(config):
    """Start watching Pinboard."""
    config.client = Client(loglevel=config.loglevel)
    client = config.client
    client.start()


@cli.command(help="Run once for a single URL.")
@pass_config
@click.argument("url", nargs=1)
def runonce(config, url):
    """Downloads a single video from <URL>."""
    config.client = Client(loglevel=config.loglevel)
    client = config.client
    client.runonce(url)


@cli.command(help="Get the current status and recent history.")
@pass_config
def status(config):
    """Get the current status and recent history."""
    config.client = Client(loglevel=config.loglevel)
    client = config.client
    client.status()


@cli.command(help="Get the history.")
@click.option("-h", "--human", is_flag=True)
@click.option("-f", "--failed-only", is_flag=True)
@pass_config
def get_history(config, human, failed_only):
    """View the history."""
    config.client = Client(loglevel=config.loglevel)
    client = config.client
    client.get_history(human, failed_only)


@cli.command(help="Delete an event from the history.")
@click.option("--all", "all_", is_flag=True)
@click.option("-u", "--url")
@pass_config
def remove_from_history(config, url, all_):
    """Remove the event for <URL> from the history."""
    config.client = Client(loglevel=config.loglevel)
    client = config.client
    client.remove_from_history(url, all_)


if __name__ == "__main__":
    cli()
