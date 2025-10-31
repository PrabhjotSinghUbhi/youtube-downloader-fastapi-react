import os
import shutil
import uuid
import base64
from threading import Lock
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YouTube Downloader")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://youtube-downloader-fastapi-react.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --- Global Variables ---
downloads = {}
downloads_lock = Lock()


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <body>
        <h2>YouTube Downloader (FastAPI + yt-dlp)</h2>
        <p>Server is up and running ✅</p>
        </body>
    </html>
    """


# --- Utility Functions ---

def cleanup_path(path: str):
    """Remove a file or directory (best-effort)."""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print("Cleanup failed:", e)


def progress_hook(download_id):
    """Track progress of yt_dlp downloads."""
    def hook(d):
        if d['status'] == 'downloading':
            with downloads_lock:
                downloads[download_id]['progress'] = d.get(
                    '_percent_str', '0%')
                downloads[download_id]['status'] = 'downloading'
        elif d['status'] == 'finished':
            with downloads_lock:
                downloads[download_id]['status'] = 'processing'
    return hook


def background_download(download_id: str, url: str, kind: str):
    """Perform the actual download in the background."""
    try:
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{download_id}.%(ext)s")

        # Decode cookies if present (base64 encoded)
        encoded_cookies = os.getenv("COOKIE_CONTENT")
        cookies_path = None
        if encoded_cookies:
            cookies_path = "cookies.txt"
            with open(cookies_path, "wb") as f:
                f.write(base64.b64decode(encoded_cookies))

        # --- Select download type ---
        if kind == "video":
            ydl_opts = {
                "cookiefile": cookies_path,
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": output_path,
                "progress_hooks": [progress_hook(download_id)],
                "quiet": True,
            }
        elif kind == "audio":
            ydl_opts = {
                "cookiefile": cookies_path,
                "format": "bestaudio/best",
                "outtmpl": output_path,
                "progress_hooks": [progress_hook(download_id)],
                "quiet": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        elif kind == "thumbnail":
            ydl_opts = {
                "cookiefile": cookies_path,
                "skip_download": True,
                "writethumbnail": True,
                "progress_hooks": [progress_hook(download_id)],
                "outtmpl": output_path,
                "quiet": True,
            }
        else:
            raise HTTPException(
                status_code=400, detail="Invalid kind parameter")

        # --- Begin download ---
        with downloads_lock:
            downloads[download_id] = {
                "status": "downloading", "path": None, "progress": "0%"}

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            with downloads_lock:
                downloads[download_id]["status"] = "finished"
                downloads[download_id]["path"] = filename

    except Exception as e:
        with downloads_lock:
            downloads[download_id] = {"status": "error", "error": str(e)}


# --- Routes ---

@app.post("/download")
def start_download(
    url: str = Form(...),
    kind: str = Form("video"),
    background_tasks: BackgroundTasks = None,
):
    """Start a download and return a tracking ID."""
    download_id = str(uuid.uuid4())
    with downloads_lock:
        downloads[download_id] = {
            "status": "starting", "path": None, "progress": "0%"}
    background_tasks.add_task(background_download, download_id, url, kind)
    return {"download_id": download_id, "status": "started"}


@app.get("/status/{download_id}")
def check_status(download_id: str):
    """Check the current status of a download."""
    with downloads_lock:
        info = downloads.get(download_id)
    if not info:
        raise HTTPException(status_code=404, detail="Download not found")
    return info


@app.get("/get-file/{download_id}")
def get_file(download_id: str, background_tasks: BackgroundTasks = None):
    """Return the downloaded file."""
    with downloads_lock:
        info = downloads.get(download_id)

    if not info or info.get("status") != "finished":
        raise HTTPException(status_code=404, detail="File not ready yet")

    file_path = info["path"]

    # --- Stream file to client ---
    def iterfile(path):
        with open(path, "rb") as f:
            while chunk := f.read(1024 * 1024):  # 1MB chunks
                yield chunk

    if background_tasks:
        background_tasks.add_task(cleanup_path, file_path)
        with downloads_lock:
            downloads.pop(download_id, None)

    return StreamingResponse(
        iterfile(file_path),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"},
    )


@app.get("/video-info")
def get_video_info(url: str = Query(..., description="YouTube video URL")):
    """Fetch video info without downloading."""
    encoded_cookies = os.getenv("COOKIE_CONTENT")
    cookies_path = None
    if encoded_cookies:
        cookies_path = "cookies.txt"
        with open(cookies_path, "wb") as f:
            f.write(base64.b64decode(encoded_cookies))

    ydl_opts = {
        "cookiefile": cookies_path,
        "quiet": True,
        "skip_download": True,
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
        "description": info.get("description"),
    }
