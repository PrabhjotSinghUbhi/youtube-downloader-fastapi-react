import { Download, Loader2 } from "lucide-react";

export const VideoPreview = ({
    videoData,
    selectedFormat,
    onDownload,
    loading,
}) => (
    <div className="bg-white rounded-xl border border-gray-200 shadow-md overflow-hidden">
        {/* Thumbnail Section */}
        <div className="relative">
            <img
                src={videoData.thumbnail}
                alt="Video thumbnail"
                className="w-full h-64 object-cover"
            />
            <div className="absolute bottom-2 right-2 bg-black bg-opacity-80 px-2 py-1 rounded text-white text-sm font-semibold">
                {videoData.duration}
            </div>
        </div>

        {/* Content Section */}
        <div className="p-6">
            {/* Title */}
            <h3 className="font-bold text-gray-900 text-xl mb-3 leading-tight">
                {videoData.title}
            </h3>

            {/* Channel Info */}
            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-gray-200">
                <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center text-white font-bold">
                    {videoData.uploader.charAt(0)}
                </div>
                <div>
                    <p className="font-semibold text-gray-900">
                        {videoData.uploader}
                    </p>
                    <p className="text-sm text-gray-600">
                        {videoData.subscribers} subscribers
                    </p>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-4 pb-4 border-b border-gray-200">
                <div>
                    <p className="text-sm text-gray-600 mb-1">Views</p>
                    <p className="font-bold text-gray-900">
                        {videoData.view_count}
                    </p>
                </div>
                <div>
                    <p className="text-sm text-gray-600 mb-1">Likes</p>
                    <p className="font-bold text-gray-900">
                        {videoData.like_count}
                    </p>
                </div>
                <div>
                    <p className="text-sm text-gray-600 mb-1">Duration</p>
                    <p className="font-bold text-gray-900">
                        {videoData.duration}
                    </p>
                </div>
            </div>

            {/* Description */}
            <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-2 text-sm">
                    Description
                </h4>
                <p className="text-sm text-gray-700 leading-relaxed line-clamp-3">
                    {videoData.description}
                </p>
            </div>

            {/* Download Button */}
            <button
                onClick={onDownload}
                className={`w-full px-6 py-4 text-white font-bold rounded-lg transition-colors shadow-lg hover:shadow-xl flex items-center justify-center gap-3 text-lg ${
                    loading ? "bg-gray-500" : "bg-red-600"
                }`}
            >
                {loading ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Processing...
                    </>
                ) : (
                    <>
                        <Download className="w-5 h-5" />
                        Download
                    </>
                )}
            </button>
        </div>
    </div>
);
