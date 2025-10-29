import { AlertCircle, Check } from "lucide-react";

export const StatusMessage = ({ type, message }) => {
    const styles = {
        success: "bg-green-50 border-green-200 text-green-800",
        error: "bg-red-50 border-red-200 text-red-800",
        info: "bg-blue-50 border-blue-200 text-blue-800",
    };

    const icons = {
        success: Check,
        error: AlertCircle,
        info: AlertCircle,
    };

    const Icon = icons[type];

    return (
        <div
            className={`rounded-lg border p-4 flex items-start gap-3 ${styles[type]}`}
        >
            <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm font-medium">{message}</p>
        </div>
    );
};
