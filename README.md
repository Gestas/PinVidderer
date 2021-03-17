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
* [Jellyfin](https://jellyfin.org/)
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
                                  in config.ini. Messages will be sent to the console.

  --help                          Show this message and exit.

Commands:
  get-history          Get the history.
  remove-from-history  Delete an event from the history.
  runonce              Run once for a single URL.
  setup                Setup PinVidderer.
  start                Start watching Pinboard.
  status               Get the current status and recent history.
```

### Adding a bookmark with a tag - 
See [https://pinboard.in/howto/#saving](https://pinboard.in/howto/#saving) for details. 
Here's the `popup` bookmarklet updated to automatically include the PinVidderer default tag, `PinVidderer` - 
```
javascript:q=location.href;if(document.getSelection){d=document.getSelection();}else{d='';};p=document.title;void(open('https://pinboard.in/add?tags=PinVidderer&noui=yes&url='+encodeURIComponent(q)+'&description='+encodeURIComponent(d)+'&title='+encodeURIComponent(p),'Pinboard','toolbar=no,width=700,height=350'));
```
And the `same page` bookmarklet - 
```
javascript:if(document.getSelection){s=document.getSelection();}else{s='';};document.location='https://pinboard.in/add?tags=PinVidderer&next=same&url='+encodeURIComponent(location.href)+'&description='+encodeURIComponent(s)+'&title='+encodeURIComponent(document.title)
```

This works on iOS - 
```
```
If you have [Post By Mail](https://pinboard.in/settings/) turned on you can include the tag in the last line of the email - 
```
To:
    secret-email-address@pinboard.in
Subject: 
    <Bookmark title>
Body: 
    <Link>
    PinVidderer
```


### Configuration file -
Is located at `<USER HOME>/.pinvidderer/config.ini` by default.
```
[PINVIDDERER]
DOWNLOAD PATH: ~/Videos    # Path to download videos to.
SOURCE TAG: Pinvidderer    # Tag to search Pinboard for.
REMOVE TAG: True    # Remove the source tag from the bookmark if the download succeeds
DELETE BOOKMARK: False    # Delete the bookmark if the download succeeds and the bookmark only has a single tag.
FORCE: False    # Ignore the history and overwrite any existing files.

# Get a thumbnail from the video source, if available.
GET FANART: True
FANART FILENAME: fanart
FANART FORMAT: jpeg

# Smart crop the thumbnail into a poster.
CREATE POSTER: True
POSTER FILENAME: poster
POSTER FORMAT: jpeg
POSTER ASPECT RATIO: 2:3

POLL INTERVAL: 300    # Frequency to check Pinboard for changes. In seconds
BACKUP FILE SUFFIX: .backup

[NFO]
CREATE: True
# There isn't a standard for how media managers handle newlines in NFO files.
# This works for Jellyfin -
PLOT PREFIX: <![CDATA[    # Prefix the plot string with this.
NEWLINE DELIMITER: <br/>    # Replace `\n` with this.
PLOT SUFFIX: ]]>     # Suffix the plot string with this.

[AUTH]
# Pinboard token can also be specified as the "PINBOARD_TOKEN" environment variable.
PINBOARD TOKEN:

[YOUTUBEDL]
# See https://github.com/ytdl-org/youtube-dl/blob/master/README.md#format-selection
FORMAT: bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best

[DEV]
LOG LEVEL: WARNING
# Youtube-dl is very verbose
YOUTUBEDL LOG LEVEL: WARNING
CONFIG DIR: ~/.pinvidderer
HISTORY FILE: history.json

```

#### PinVidderer default downloaded video format -
The default youtube-dl video format string is `bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best`. This will download the highest quality available video and audio, preferring .mp4 and excluding .webm. It's still possible to get a .mkv output file. This also avoids post-download transcoding.
See [https://github.com/ytdl-org/youtube-dl/issues/4886#issuecomment-334068157](https://github.com/ytdl-org/youtube-dl/issues/4886#issuecomment-334068157) for a more complete explanation.
If you always want the highest quality video and don't care about the output format set `FORMAT` in the config.ini file to `bestvideo+bestaudio/best`.
See [FORMAT SELECTION](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#format-selection) in the youtube-dl documentation for more options.


** [https://old.reddit.com/r/DataHoarder/](https://old.reddit.com/r/DataHoarder/)