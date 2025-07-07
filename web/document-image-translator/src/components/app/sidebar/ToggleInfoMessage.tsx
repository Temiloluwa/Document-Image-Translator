"use client";

import React from "react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";
import { Info } from "lucide-react";

export default function ToggleInfoMessage() {
  const { uploadStatus } = useImageTranslatorContext();
  if (uploadStatus !== "completed") return null;
  return (
    <div className="w-full flex items-center gap-2 mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg shadow-sm animate-fade-in">
      <Info className="w-5 h-5 text-blue-500 flex-shrink-0" />
      <span className="text-sm text-blue-800 font-medium">
        <strong>Tip:</strong> Toggle the switch at the <span className="underline">top right</span> to view your translated result.
      </span>
    </div>
  );
}
