import React, { useState } from "react";
import {
    Download,
    Video,
    Music,
    Image,
    Check,
    AlertCircle,
    Loader2,
    Icon,
} from "lucide-react";
import Header from "./Header";
import { FormatCard } from "./FormatCard";
import { StatusMessage } from "./StatusMessage";
import { VideoPreview } from "./VideoPreview";

function YouTubeDownloader() {
    const [url, setUrl] = useState("");
    const [selectedFormat, setSelectedFormat] = useState("video");
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState(null);
    const [videoData, setVideoData] = useState(null);

    const formats = [
        {
            format: "video",
            icon: Video,
            title: "Video (MP4)",
            description: "Download full video with audio in MP4 format",
        },
        {
            format: "audio",
            icon: Music,
            title: "Audio (MP3)",
            description: "Extract and download audio only in MP3 format",
        },
        {
            format: "thumbnail",
            icon: Image,
            title: "Thumbnail",
            description: "Download video thumbnail in high quality",
        },
    ];

    const handleFetchInfo = async () => {
        try {
            setLoading(true);
            const resp = await fetch(
                `http://127.0.0.1:8000/video-info?url=${url}`,
                {
                    method: "GET",
                }
            );
            const data = await resp.json();
            console.log(data);
            setVideoData(data);
        } catch (error) {
            console.log("Error in Fetching the youtube info: ", error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async () => {
        if (!url.trim()) {
            setStatus({
                type: "error",
                message: "Please enter a valid YouTube URL",
            });
            return;
        }

        setLoading(true);
        setStatus(null);

        try {
            const formData = new FormData();
            formData.append("url", url);
            formData.append("kind", selectedFormat);

            console.log(formData);

            const response = await fetch("http://127.0.0.1:8000/download", {
                method: "POST",
                body: formData,
            });

            console.log(response);

            if (!response.ok) {
                throw new Error("Download failed");
            }

            // Convert response to blob (binary data)
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);

            // Trigger browser download
            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = selectedFormat === "video" ? "video.mp4" : "audio.mp3";
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            console.error(err);
            alert("Something went wrong during download.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 ">
            <Header />

            <main className="max-w-6xl mx-auto px-4 py-8">
                {/* URL Input Section */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                    <label className="block text-sm font-semibold text-gray-900 mb-3">
                        Enter YouTube URL
                    </label>
                    <div className="flex sm:flex-row gap-3 flex-col">
                        <input
                            type="text"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            placeholder="https://www.youtube.com/watch?v=..."
                            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        />
                        <button
                            onClick={handleFetchInfo}
                            disabled={loading}
                            className="px-8 py-3 bg-red-600 text-center text-white font-semibold rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <Download className="w-5 h-5" />
                                    Fetch
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Format Selection */}
                <div className="mb-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">
                        Select Format
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {formats.map((format) => (
                            <FormatCard
                                key={format.format}
                                {...format}
                                selected={selectedFormat}
                                onClick={setSelectedFormat}
                            />
                        ))}
                    </div>
                </div>

                {/* Status Message */}
                {status && (
                    <div className="mb-6">
                        <StatusMessage
                            type={status.type}
                            message={status.message}
                        />
                    </div>
                )}

                {/* Video Preview */}
                {videoData && (
                    <div className="mb-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            Preview
                        </h2>
                        <VideoPreview
                            videoData={videoData}
                            selectedFormat={selectedFormat}
                            onDownload={handleDownload}
                            loading={loading}
                        />
                    </div>
                )}

                {/* Info Section */}
                <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
                    <h3 className="font-semibold text-blue-900 mb-2">
                        How to use
                    </h3>
                    <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                        <li>Copy the YouTube video URL from your browser</li>
                        <li>Paste it into the input field above</li>
                        <li>
                            Select your preferred format (Video, Audio, or
                            Thumbnail)
                        </li>
                        <li>Click "Fetch" to process the video</li>
                        <li>Click the download button to save the file</li>
                    </ol>
                </div>
            </main>
        </div>
    );
}

export default YouTubeDownloader;
