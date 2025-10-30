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
    """Remove a file or directory (best-effort)."""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
    except Exception as e:
        # log in real app
        print("Cleanup failed:", e)


def my_hook(d):
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
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'retries': 5,             # retry up to 5 times
        'socket_timeout': 30,     # wait up to 30s per connection
        'fragment_retries': 10,   # retry on partial download
        'skip_unavailable_fragments': True,
        'format': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst',
        'ffmpeg_location': r"D:\Downloads\myDownloads\ffmpeg\bin",
        'progress_hooks': [my_hook],
    }

    if kind == 'audio':
        # postprocessor to extract audio and convert to mp3
        opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # result file ext will be .mp3 due to postprocessor
        })

    return opts


@app.post("/download")
def download_video(url: str = Form(...), kind: str = Form("video")):
    download_id = str(uuid.uuid4())
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{download_id}.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best" if kind == "video" else "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "ffmpeg_location": r"D:\Downloads\myDownloads\ffmpeg\bin",  # path if needed
        "noplaylist": True,
    }

    if kind == "thumbnail":
        ydl_opts.update({
            "skip_download": True,
            "writethumbnail": True,
        })

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            if kind == "thumbnail":
                thumb_exts = [".jpg", ".png", ".webp"]
                for ext in thumb_exts:
                    possible_thumb = filename.rsplit(".", 1)[0] + ext
                    if os.path.exists(possible_thumb):
                        filename = possible_thumb
                        break
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Download failed: {str(e)}")

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
