# PinVidderer 
### A Bookmarked Video Downloader
Horribly abuse Pinboard as a messaging queue to make downloading videos from the Internet easier.

### Why Pinboard?
Pinboard makes to easy to add bookmarks from any device or browser which makes it a good tool for passing URLs around.
See [Saving Bookmarks on Pinboard.in](https://pinboard.in/faq/#saving_bookmarks) and [Saving Bookmarks for Downloading Videos]() below.

### Why?
Sometimes I want a local copy** of a video I've found, this makes that easy. 
To make consuming the videos easier you can point any one of several local media managers to the download folder. 
The `get-thumbnail` and `create-nfo` options can be useful if you do this. Popular media managers include -
* [Kodi](https://kodi.tv/)
* [Emby](https://emby.media/)
* [Plex](https://www.plex.tv/)
* [Jellyfin.org](https://jellyfin.org/)
* [Streama](https://github.com/streamaserver/streama)

### Details -
This tool polls the Pinboard API looking for bookmarks with a specific tag.  Once a bookmark with that tag is found it uses [the Youtube-dl application](https://ytdl-org.github.io/youtube-dl/index.html) to download the video.
Optionally downloads a thumbnail and creates a .nfo file. 

### Install - 
**NOTE:** Using `pipx` is strongly recommended, https://pypi.org/project/pipx/.
Pipx will create the required virtualenv and ensure that `PinVidderer` is in your path. 
```
$ pipx install git+https://github.com/Gestas/PinVidderer
$ PinVidderer setup
```
### Usage -
```
$ PinVidderer 
Usage: PinVidderer [OPTIONS] COMMAND [ARGS]...

  A Bookmarked Video Downloader.

Options:
  --loglevel [ERROR|WARNING|INFO|DEBUG|CRITICAL]
                                  Sets the logging level, overriding the value
                                  in config.ini

  --help                          Show this message and exit.

Commands:
  get-history          Get the history.
  remove-from-history  Delete an event from the history.
  runonce              Run once for a single URL.
  setup                Setup PinVidderer.
  start                Start watching Pinboard.
  status               Get the current status and recent history.
```

#### Default downloaded video format -
The default youtube-dl video format string is `bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best`. This will download the highest quality available video and audio, preferring .mp4 and excluding .webm. It's still possible to get a .mkv output file. This also avoids post-download transcoding.
See [https://github.com/ytdl-org/youtube-dl/issues/4886#issuecomment-334068157](https://github.com/ytdl-org/youtube-dl/issues/4886#issuecomment-334068157) for a more complete explanation.
If you always want the highest quality video and don't care about the output format set `FORMAT` in the config.ini file to `bestvideo+bestaudio/best`.
See [FORMAT SELECTION](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#format-selection) in the youtube-dl documentation for more options.

** [https://old.reddit.com/r/DataHoarder/](https://old.reddit.com/r/DataHoarder/)