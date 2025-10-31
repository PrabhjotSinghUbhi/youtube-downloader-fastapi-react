import os
import shutil
import uuid
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import base64
load_dotenv()

app = FastAPI(title="Youtube Downloader")

app.add_middleware(
    CORSMiddleware,
    # or ["http://localhost:5173"] for security
    allow_origins=["https://youtube-downloader-fastapi-react.vercel.app",
                   "https://youtube-downloader-fastapi-react.vercel.app/",
                   "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <body>
        <h2>YouTube Downloader (FastAPI + yt-dlp) root working</h2>
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


@app.post("/download")
def download_video(url: str = Form(...), kind: str = Form("video"), background_tasks: BackgroundTasks = None):
    download_id = str(uuid.uuid4())
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{download_id}.%(ext)s")

    encoded_cookies = os.getenv("COOKIE_CONTENT")

    if encoded_cookies:
        cookies_path = "cookies.txt"
        with open(cookies_path, "wb") as f:
            f.write(base64.b64decode(encoded_cookies))
    else:
        cookies_path = None  # fallback if not set

    if kind == "video":
        ydl_opts = {
            "cookiefile": cookies_path,
            "format": "bestvideo+bestaudio/best",
            "outtmpl": output_path,
            "quiet": True,
            # "ffmpeg_location": r"D:\Downloads\myDownloads\ffmpeg\bin",
            "noplaylist": True
        }
    elif kind == "audio":
        ydl_opts = {
            "cookiefile": cookies_path,
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "quiet": True,
            # "ffmpeg_location": r"D:\Downloads\myDownloads\ffmpeg\bin",
            "noplaylist": True,
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
        }
    elif kind == "thumbnail":
        ydl_opts = {
            "cookiefile": cookies_path,
            "skip_download": True,      # only download metadata, not video/audio
            "writeinfojson": False,     # no .json file
            "writethumbnail": True,     # <-- actually download the thumbnail
            "outtmpl": output_path,
            "quiet": True,
            'postprocessors': [
                {
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                }
            ]
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid kind parameter")

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        if kind == "thumbnail":
            # yt-dlp saves thumbnail as .jpg or .webp next to outtmpl
            thumbnail_path = None
            for ext in ("jpg", "png", "webp"):
                test_path = output_path.replace("%(ext)s", ext)
                if os.path.exists(test_path):
                    thumbnail_path = test_path
                    break
            if not thumbnail_path:
                raise HTTPException(
                    status_code=404, detail="Thumbnail not found")
            if background_tasks:
                background_tasks.add_task(cleanup_path, thumbnail_path)
            return FileResponse(thumbnail_path, filename=os.path.basename(thumbnail_path))

        # otherwise handle video/audio
        filename = ydl.prepare_filename(info)
        if background_tasks:
            background_tasks.add_task(cleanup_path, filename)
        return FileResponse(filename, filename=os.path.basename(filename))


@app.get("/video-info")
def get_video_info(url: str = Query(..., description="YouTube video URL")):

    encoded_cookies = os.getenv("COOKIE_CONTENT")

    if encoded_cookies:
        cookies_path = "cookies.txt"
        with open(cookies_path, "wb") as f:
            f.write(base64.b64decode(encoded_cookies))
    else:
        cookies_path = None  # fallback if not set

    ydl_opts = {
        "cookiefile": cookies_path,
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
