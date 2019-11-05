# ytdl: My Youtube Downloader

_Last modified: 8/13/2017_

Prerequistes:

- youtube-dl: https://github.com/rg3/youtube-dl
- ffmpeg: http://ffmpeg.org/

Deployment procedure:
    
- Step 1. Install youtube-dl
    - Run: `sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl`
    - Run: `sudo chmod a+rx /usr/local/bin/youtube-dl`
- Step 2. Install ffmpeg
    - Download `ffmpeg-xxx.tar.xz` from https://www.johnvansickle.com/ffmpeg/
    - Extract to `~/ffmpeg/`: https://askubuntu.com/a/107976
    - Add `~/ffmpeg/` to `$PATH`: https://www.computerhope.com/issues/ch001647.htm
