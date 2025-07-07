import React from "react";
import { ToggleLeft, ToggleRight } from "lucide-react";

type HeaderToggleProps = {
  showTranslated: boolean;
  canToggle: boolean;
  onToggle: () => void;
};

export default function HeaderToggle({ showTranslated, canToggle, onToggle }: HeaderToggleProps) {
  return (
    <div className="bg-white border-b border-gray-200 p-4 flex justify-between items-center">
      <h2 className="text-lg font-semibold text-gray-900">
        {showTranslated ? "Translated Document" : "Original Document"}
      </h2>
      {canToggle && (
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Original</span>
          <button onClick={onToggle} className="p-1">
            {showTranslated ? (
              <ToggleRight className="w-8 h-8 text-blue-600" />
            ) : (
              <ToggleLeft className="w-8 h-8 text-gray-400" />
            )}
          </button>
          <span className="text-sm text-gray-600">Translated</span>
        </div>
      )}
    </div>
  );
}
