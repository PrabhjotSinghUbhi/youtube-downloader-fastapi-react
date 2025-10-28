# 🎥 YouTube Downloader — FastAPI + React

A full-stack web application that lets users download YouTube videos or extract audio (MP3) directly from a YouTube URL.  
Built using **FastAPI** for the backend and **React** for the frontend.

---

## 🚀 Features

- 🎧 Download **audio (MP3)** or **video (MP4)** formats  
- 🖼️ Fetch video **title, thumbnail, uploader, and duration**  
- 🌐 Fast and lightweight **FastAPI backend**  
- ⚛️ Simple and responsive **React frontend**  
- 💾 Direct browser download (no annoying file popups)  

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React (Vite or CRA) |
| **Backend** | FastAPI (Python) |
| **Downloader Engine** | yt-dlp + ffmpeg |
| **HTTP Client** | Axios / Fetch |
| **Runtime** | Node.js & Python 3.10+ |

---

## ⚙️ Project Structure

```
youtube-downloader-fastapi-react/
│
├── backend/
│   ├── main.py              # FastAPI app (API endpoints)
│   ├── requirements.txt     # Python dependencies
│   └── downloads/           # Folder where temporary files are stored
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React main component
│   │   └── components/      # Additional UI components
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🧰 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/youtube-downloader-fastapi-react.git
cd youtube-downloader-fastapi-react
```

---

### 2. Backend Setup (FastAPI)

#### 🐍 Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows
```

#### 📦 Install Dependencies
```bash
pip install fastapi uvicorn yt-dlp ffmpeg-python
```

#### ▶️ Run the Backend
```bash
uvicorn main:app --reload
```
By default, it runs at: **http://localhost:8000**

---

### 3. Frontend Setup (React)

```bash
cd ../frontend
npm install
npm run dev
```

React will start on **http://localhost:5173** (or similar port).

---

## 🔄 How It Works

1. User enters a **YouTube video URL** in the React app.  
2. The frontend calls the FastAPI backend:
   - `/video-info` → Fetches video title, thumbnail, duration, etc.  
   - `/download` → Downloads audio/video and triggers browser download.  
3. FastAPI uses **yt-dlp** internally (and **ffmpeg** for audio extraction).  

---

## 🧠 Example API Routes

| Route | Method | Description |
|--------|---------|-------------|
| `/video-info?url=...` | GET | Fetch video details |
| `/download?url=...&format=video` | GET | Download MP4 video |
| `/download?url=...&format=audio` | GET | Download MP3 audio |

---

## 🖼️ UI Preview

*(Add screenshots here once your frontend UI is ready!)*

---

## 💡 Future Enhancements

- ⏱️ Show download progress bar  
- 📱 Make the UI mobile-friendly  
- 🗃️ Add format/quality selector (360p, 720p, etc.)  
- 🌍 Deploy backend to Render / Railway and frontend to Vercel  

---

## 🧑‍💻 Author

**Prince**  
Software Engineer | Web Developer | MERN + FastAPI Enthusiast  
[GitHub](https://github.com/PrabhjotSinghUbhi) | [LinkedIn](https://linkedin.com/in/prabhjotsinghubhif)

---

## ⚠️ Disclaimer
This project is for **educational purposes only**. Downloading copyrighted content without permission may violate YouTube’s Terms of Service.
