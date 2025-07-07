"use client";

import React from "react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";


export default function UploadButton() {
  const {
    handleUpload,
    canUpload,
    uploadStatus,
    showTranslated,
    handleReset,
    setShowTranslated,
  } = useImageTranslatorContext();


  const getButtonText = () => {
    if (showTranslated) return "Translate New File";
    switch (uploadStatus) {
      case "uploading":
        return "Uploading...";
      case "processing":
        return "Processing...";
      default:
        return "Translate File";
    }
  };

  return (
    <button
      onClick={() => {
        if (showTranslated) {
          // Reset the app state for a new translation
          if (typeof setShowTranslated === 'function') setShowTranslated(false);
          handleReset();
        } else {
          handleUpload();
        }
      }}
      disabled={!canUpload && !showTranslated}
      className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
        (canUpload || showTranslated)
          ? "bg-blue-600 text-white hover:bg-blue-700 cursor-pointer"
          : "bg-gray-300 text-gray-500 cursor-not-allowed"
      }`}
      style={{ cursor: (canUpload || showTranslated) ? 'pointer' : 'not-allowed' }}
    >
      {getButtonText()}
    </button>
  );
}
