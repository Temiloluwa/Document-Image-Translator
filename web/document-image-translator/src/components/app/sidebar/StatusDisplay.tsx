"use client";

import React from "react";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";

export default function StatusDisplay() {
  const { uploadStatus, processingProgress, errorMessage, handleReset, handleUpload } = useImageTranslatorContext();

  if (uploadStatus === "idle") return null;

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case "uploading":
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case "processing":
        return <Loader2 className="w-4 h-4 animate-spin text-yellow-500" />;
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (uploadStatus) {
      case "uploading":
        return "Uploading file...";
      case "processing":
        return `Processing... ${processingProgress}%`;
      case "completed":
        return "Translation completed!";
      case "error":
        return errorMessage;
      default:
        return "";
    }
  };

  return (
    <div className="mb-6 w-full">
      <div className="flex items-center space-x-2 mb-2">
        {getStatusIcon()}
        <span className="text-sm font-medium text-gray-700">
          {getStatusText()}
        </span>
      </div>
      {uploadStatus === "processing" && (
        <div className="w-full flex flex-col items-stretch">
          <div className="relative" style={{ width: '100%' }}>
            <div className="bg-gray-200 rounded-full h-3 w-full" />
            <div
              className={
                `rounded-full h-3 absolute top-0 left-0 transition-all duration-300 ` +
                (processingProgress < 30
                  ? 'bg-yellow-400'
                  : processingProgress < 50
                  ? 'bg-yellow-300'
                  : processingProgress < 75
                  ? 'bg-lime-300'
                  : processingProgress < 90
                  ? 'bg-green-400'
                  : 'bg-green-600')
              }
              style={{
                width: `${processingProgress}%`,
                minWidth: 0,
                maxWidth: '100%',
                height: '100%',
                zIndex: 1
              }}
            />
          </div>
        </div>
      )}
      {uploadStatus === "error" && (
        <div className="mt-3 flex gap-2">
          <button
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
            onClick={handleReset}
          >
            Reset
          </button>
          <button
            className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-xs"
            onClick={handleUpload}
          >
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
