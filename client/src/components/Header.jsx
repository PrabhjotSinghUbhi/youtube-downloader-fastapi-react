import { Download } from "lucide-react";

const Header = () => (
    <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
            <div className="flex items-center gap-3">
                <div className="bg-red-600 p-2 rounded-lg">
                    <Download className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                        YouTube Downloader
                    </h1>
                    <p className="text-sm text-gray-600">
                        Download videos, audio, and thumbnails
                    </p>
                </div>
            </div>
        </div>
    </header>
);

export default Header;
