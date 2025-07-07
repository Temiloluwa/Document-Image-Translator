"use client";

import React from "react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";

export default function PreviewToggle() {
  const { showTranslated, setShowTranslated, canToggle } = useImageTranslatorContext();

  return (
    <div className="flex items-center justify-end w-full">
      {canToggle && (
        <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setShowTranslated(false)}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors cursor-pointer ${
              !showTranslated
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Original
          </button>
          <button
            onClick={() => setShowTranslated(true)}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors cursor-pointer ${
              showTranslated
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Translated
          </button>
        </div>
      )}
    </div>
  );
}
