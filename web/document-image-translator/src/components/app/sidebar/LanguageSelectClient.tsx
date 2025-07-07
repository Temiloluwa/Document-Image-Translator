"use client";


import React from "react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";

export default function LanguageSelectClient() {
  const { targetLanguage, setTargetLanguage, languages, uploadStatus } = useImageTranslatorContext();

  // Always allow language selection unless uploading/processing
  // If you want to visually indicate that language will be used for next upload, show a helper text
  return (
    <>
      <select
        value={targetLanguage}
        onChange={(e) => setTargetLanguage(e.target.value)}
        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-800 bg-white text-base md:text-lg"
        // Only disable during upload/processing, never based on file selection
        disabled={uploadStatus === "uploading" || uploadStatus === "processing"}
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code} className="text-gray-800 bg-white text-base md:text-lg">
            {lang.name}
          </option>
        ))}
      </select>
      {/* No hint about file selection, language can always be picked */}
    </>
  );
}
