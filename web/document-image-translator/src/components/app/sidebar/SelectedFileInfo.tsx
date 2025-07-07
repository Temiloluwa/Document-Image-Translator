"use client";

import React from "react";
import { Image, FileText } from "lucide-react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";

export default function SelectedFileInfo() {
  const { selectedFile, isFileSelected, formatFileSize } = useImageTranslatorContext();

  if (!isFileSelected || !selectedFile) return null;

  return (
    <div className="mb-6">
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center mb-2">
          {selectedFile.type.startsWith("image/") ? (
            <Image className="w-5 h-5 text-blue-500 mr-2" role="img" aria-label="image icon" />
          ) : (
            <FileText className="w-5 h-5 text-red-500 mr-2" role="img" aria-label="file icon" />
          )}
          <span
            className="font-medium text-gray-900 truncate"
            style={{ maxWidth: '14rem', display: 'inline-block', verticalAlign: 'bottom' }}
            title={selectedFile.name}
          >
            {selectedFile.name}
          </span>
        </div>
        <p className="text-sm text-gray-600">
          {formatFileSize(selectedFile.size)}
        </p>
      </div>
    </div>
  );
}
