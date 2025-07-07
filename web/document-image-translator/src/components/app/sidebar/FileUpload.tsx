"use client";

import React from "react";
import { Upload } from "lucide-react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";

export default function FileUpload() {
  const {
    handleDrop,
    handleDragOver,
    handleFileInputChange,
    fileInputRef
  } = useImageTranslatorContext();

  return (
    <div className="mb-6">
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer bg-gray-50"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className="w-10 h-10 text-blue-400 mx-auto mb-2" />
        <p className="text-gray-700 text-base font-medium mb-1">
          Upload an image or PDF to translate
        </p>
        <p className="text-gray-500 text-sm mb-1">
          Drag & drop here or <span className="text-blue-600 font-semibold">browse</span>
        </p>
        <p className="text-xs text-gray-400">
          JPEG, PNG, WebP, PDF &middot; Max 10MB
        </p>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.webp,.pdf"
        onChange={handleFileInputChange}
        className="hidden"
      />
    </div>
  );
}
