import { Check, Icon } from "lucide-react";

export const FormatCard = ({
    title,
    description,
    format,
    selected,
    onClick,
}) => (
    <button
        onClick={() => onClick(format)}
        className={`p-4 rounded-xl border-2 transition-all text-left w-full ${
            selected === format
                ? "border-red-600 bg-red-50 shadow-md"
                : "border-gray-200 hover:border-red-300 hover:shadow-sm"
        }`}
    >
        <div className="flex items-start gap-3">
            <div
                className={`p-2 rounded-lg ${
                    selected === format ? "bg-red-600" : "bg-gray-100"
                }`}
            >
                {/* <Icon
                    className={`w-5 h-5 ${
                        selected === format ? "text-white" : "text-gray-700"
                    }`}
                /> */}
            </div>
            <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{title}</h3>
                <p className="text-sm text-gray-600 mt-1">{description}</p>
            </div>
            {selected === format && (
                <Check className="w-5 h-5 text-red-600 flex-shrink-0 mt-1" />
            )}
        </div>
    </button>
);
