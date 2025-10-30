import os
import shutil
import tempfile
import uuid
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL

app = FastAPI(title="Youtube Downloader")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <body>
        <h2>YouTube Downloader (FastAPI + yt-dlp)</h2>
        <form action="/download" method="post">
            URL: <input name="url" type="text" style="width:400px"/><br/>
            Type:
            <select name="kind">
            <option value="video">Video (mp4)</option>
            <option value="audio">Audio (mp3)</option>
            </select><br/><br/>
            <button type="submit">Download</button>
        </form>
        </body>
    </html>"""


def cleanup_path(path: str):
    """
    Remove a file or directory (best-effort).

    ? os.path.isdir(path) -> checks if the given path is a directory.
    ? shutil.rmtree(path) -> removes if the it is a directory.

    ? os.path.exists(path) -> checks if the given path is a file.
    ? os.remove(path) -> removes the file.

    """
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
    except Exception as e:
        # log in real app
        print("Cleanup failed:", e)


def my_hook(d):
    """Tracks the Progress of the video being downloaded from yt-dlp.

    Args:
        d (Dictionary): 
        {
            'status': 'downloading',
            '_percent_str': ' 42.3%',
            'filename': 'video.mp4',
            'downloaded_bytes': 1048576
        }
    """
    if d['status'] == 'downloading':
        print("Downloaded", d.get('_percent_str'))
    elif d['status'] == 'finished':
        print("Finished, now post-processing")


def build_ydl_opts(output_template: str, kind: str):
    """
    Return yt-dlp options.
    output_template: path template like '/tmp/downloads/%(title)s.%(ext)s'
    kind: 'video' or 'audio'
    """
    opts = {
        # the output filename template.
        'outtmpl': output_template,

        # force downloading a single video only, even if the URL points to a playlist. Prevents yt-dlp from iterating over playlist items.
        'noplaylist': True,

        # suppress most yt-dlp console output. Useful when you want only your progress hook messages or silent operation.
        'quiet': True,

        # suppress non-fatal warnings.
        'no_warnings': True,

        # number of times to retry entire download if it fails. This is a top-level retries count.
        'retries': 5,             # retry up to 5 times

        # how many seconds to wait for network/socket operations before timing out (units = seconds). Helps avoid hanging on slow connections.
        'socket_timeout': 30,     # wait up to 30s per connection

        # for fragmented downloads (e.g., DASH/HLS segments), retry up to this many times per fragment. Useful for unstable network or missing fragments.
        'fragment_retries': 10,   # retry on partial download

        # if some fragments are unavailable (e.g., temporarily missing), skip them instead of failing the whole download. May produce broken output if too many fragments are missing, but increases robustness.
        'skip_unavailable_fragments': True,

        # This is a format selection expression that tells yt-dlp which stream(s) to pick.
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/worst',

        # Where yt-dlp will look for ffmpeg/ffprobe binaries to merge or postprocess files.
        'ffmpeg_location': r"D:\Downloads\myDownloads\ffmpeg\bin",

        # A list of callables that yt-dlp will invoke with a status dictionary during the download lifecycle.
        'progress_hooks': [my_hook],

        #  also download thumbnails
        'writethumbnail': True,
    }

    if kind == 'audio':
        # postprocessor to extract audio and convert to mp3
        # a list of postprocessor dicts. yt-dlp runs them after downloading (and after merging if needed).
        opts.update({
            'postprocessors': [{
                # tells yt-dlp to run ffmpeg to extract audio from the downloaded file(s).
                'key': 'FFmpegExtractAudio',

                # convert audio to MP3 format.
                'preferredcodec': 'mp3',

                # target bitrate for MP3 is 192 kbps. (yt-dlp/ffmpeg interpret this as kbps for most audio converters.)
                'preferredquality': '192',
            }, {
                'key': 'EmbedThumbnail'
            }, {
                'key': 'FFmpegMetadata'
            }],
            # result file ext will be .mp3 due to postprocessor
        })
    else:
        # for video, optionally convert thumbnail to jpg
        opts.update({
            'postprocessors': [
                {
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                }
            ]
        })

    return opts


@app.post("/download")
def download_video(url: str = Form(...), kind: str = Form("video")):
    """
        url and kind are form fields -> (data sent by the frontend using FormData or HTML forms).
        Form(...) tells FastAPI to read these values from form input, not JSON.
        The "..." means the url field is required.
        kind defaults to "video" — you can also send "audio" if you want to download only audio.
    """
    download_id = str(
        uuid.uuid4())  # uuid.uuid4() generates a unique random identifier,

    output_dir = "downloads"

    # Sets the folder name where files will be saved.
    os.makedirs(output_dir, exist_ok=True)
    # creates the folder if it doesn’t already exist, so the app won’t crash if it’s already there.
    # %(ext)s part is a yt-dlp template placeholder that gets replaced with the actual file extension (.mp4, .mp3, etc.) once the download finishes.
    output_path = os.path.join(output_dir, f"{download_id}.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best" if kind == "video" else "bestaudio/best",

        # File path template (the one you created above).
        "outtmpl": output_path,

        "quiet": True,
        "ffmpeg_location": r"D:\Downloads\myDownloads\ffmpeg\bin",  # path if needed
        "noplaylist": True,
    }

    try:
        # Creates a YoutubeDL object using your options.
        with YoutubeDL(ydl_opts) as ydl:
            # Calls extract_info()
            # -> url → the YouTube link.
            # -> download=True → actually downloads the file (if False, it only fetches metadata).
            info = ydl.extract_info(url, download=True)
            print(info)

            # This converts the info into the final file path (e.g. downloads/6f9b9e7e.mp4).
            filename = ydl.prepare_filename(info)
            print(filename)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail=f"Download failed: {str(e)}")

    # FileResponse is a FastAPI class that sends a file as a response so the browser downloads it directly.
    return FileResponse(filename, filename=os.path.basename(filename))


@app.get("/video-info")
def get_video_info(url: str = Query(..., description="YouTube video URL")):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,  # <-- Don't download video, just get info
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "description": info.get("description")
    }
