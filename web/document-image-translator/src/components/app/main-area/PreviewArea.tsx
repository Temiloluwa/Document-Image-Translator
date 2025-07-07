"use client";

import React, { useEffect, useState } from "react";
import "./preview.css";
// import Image from "next/image";
import { FileText } from "lucide-react";
import { useImageTranslatorContext } from "@/providers/ImageTranslatorProvider";


export default function PreviewArea() {
  const {
    selectedFile,
    isFileSelected,
    previewUrl,
    showTranslated,
    errorMessage,
    uploadStatus,
    handleReset,
    translatedHtml,
  } = useImageTranslatorContext();

  // State to hold extracted head and body from translatedHtml
  const [extractedHead, setExtractedHead] = useState<string>("");
  const [extractedBody, setExtractedBody] = useState<string>("");

  // Effect to extract head and body from translatedHtml
  useEffect(() => {
    if (translatedHtml) {
      // Use DOMParser to extract head and body
      try {
        const parser = new window.DOMParser();
        const doc = parser.parseFromString(translatedHtml, "text/html");
        setExtractedHead(doc.head.innerHTML || "");
        setExtractedBody(doc.body.innerHTML || "");
      } catch {
        setExtractedHead("");
        setExtractedBody(translatedHtml); // fallback
      }
    } else {
      setExtractedHead("");
      setExtractedBody("");
    }
  }, [translatedHtml]);

  // Clipboard paste handler for images
  const { handleFileInputChange } = useImageTranslatorContext();
  // Listen for paste events on the whole window for image clipboard
  React.useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      if (e.clipboardData) {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
          const item = items[i];
          if (item.type.startsWith("image/")) {
            const file = item.getAsFile();
            if (file) {
              // Simulate file input change event
              const dt = new DataTransfer();
              dt.items.add(file);
              const event = { target: { files: dt.files } } as React.ChangeEvent<HTMLInputElement>;
              handleFileInputChange(event);
            }
          }
        }
      }
    };
    window.addEventListener('paste', handlePaste as EventListener);
    return () => { window.removeEventListener('paste', handlePaste as EventListener); };
  }, [handleFileInputChange]);

  if (!isFileSelected) {
    return (
      <div className="flex-1 p-6 overflow-auto">
        <div className="h-full flex items-center justify-center min-h-[350px]">
          <div className="flex flex-col items-center justify-center w-full max-w-xs mx-auto text-center relative">
            {/* Centered arrow and label */}
            <div className="flex flex-col items-center mb-8">
              <svg width="80" height="80" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className="animate-bounce-slow drop-shadow-lg">
                <defs>
                  <linearGradient id="arrowGradientCenter" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#3b82f6" />
                    <stop offset="1" stopColor="#60a5fa" />
                  </linearGradient>
                </defs>
                <circle cx="32" cy="32" r="30" fill="#e0f2fe" />
                <path d="M48 32H16M16 32l12-12M16 32l12 12" stroke="url(#arrowGradientCenter)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <div className="mt-3 text-blue-600 font-semibold text-base text-center whitespace-nowrap">
                Start by selecting a document
              </div>
              <div className="text-blue-400 font-normal text-sm mt-1 mb-6">(see left sidebar)</div>
              <div className="text-gray-500 font-medium text-base mb-4">or</div>
            </div>
            {/* Paste from clipboard icon and text */}
            <svg xmlns="http://www.w3.org/2000/svg" className="w-16 h-16 text-blue-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <rect x="4" y="4" width="16" height="16" rx="3" className="stroke-current text-blue-300" fill="#e0f2fe" />
              <path d="M8 14l2.5-3 2.5 3 3.5-5 3.5 5" className="stroke-blue-500" strokeWidth="1.5" fill="none" />
              <circle cx="9" cy="9" r="1.2" className="fill-blue-400" />
            </svg>
            <p className="text-lg font-semibold text-gray-800 mb-1 cursor-pointer hover:text-blue-600 transition-colors">Paste from your clipboard</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-2 sm:p-4 md:p-6 overflow-auto w-full">
      <div className="h-full flex flex-col items-center justify-center relative w-full">
        {/* Error message and retry button (no reset on success, only on error) */}
        {uploadStatus === "error" && errorMessage && (
          <div className="mb-4 text-center">
            <p className="text-red-500 font-medium mb-2">{errorMessage}</p>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              style={{ cursor: "pointer" }}
              onClick={handleReset}
            >
              Retry / Reupload
            </button>
          </div>
        )}

        {/* Translate New File button removed from viewing area as per user request */}

        <div className="flex-1 flex items-center justify-center w-full">
          {showTranslated ? (
            <div className="w-full h-full bg-white rounded-lg shadow-sm border border-gray-200 p-2 sm:p-4 overflow-auto">
              <div className="flex justify-end mb-2">
                {/* Print as PDF button always visible when showTranslated */}
                <button
                  className="px-3 py-1 bg-gray-100 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-200 transition-colors"
                  onClick={() => {
                    const printWindow = window.open('', '_blank');
                    if (printWindow) {
                      printWindow.document.write(`<!DOCTYPE html><html><head>${extractedHead}</head><body>${extractedBody}</body></html>`);
                      printWindow.document.close();
                      printWindow.focus();
                      printWindow.print();
                    }
                  }}
                  disabled={!translatedHtml}
                  style={{ opacity: translatedHtml ? 1 : 0.5, cursor: translatedHtml ? 'pointer' : 'not-allowed' }}
                >
                  Print as PDF
                </button>
              </div>
              {translatedHtml ? (
                <>
                  {/* Inject styles from head, but filter out html/body/global font/zoom/scale/size changes */}
                  {/* Use custom A4 preview styles */}
                  <div className="translated-html-preview" style={{ minHeight: 400 }}>
                    <div dangerouslySetInnerHTML={{ __html: extractedBody }} />
                  </div>
                </>
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center">
                  <p className="text-gray-500">Loading translated HTML...</p>
                  <p className="text-xs text-gray-400 mt-2">If this takes too long, please try again or check your network.</p>
                </div>
              )}
            </div>
          ) : previewUrl ? (
            // ...existing code...
            <div className="w-full max-w-2xl md:max-w-4xl max-h-full">
              {selectedFile?.type.startsWith("image/") ? (
                <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={previewUrl || ""}
                    alt="Preview"
                    style={{
                      maxWidth: '100%',
                      maxHeight: '80vh',
                      height: 'auto',
                      width: 'auto',
                      borderRadius: '.5rem',
                      boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                      display: 'block',
                      margin: '0 auto',
                    }}
                    loading="lazy"
                  />
                </div>
              ) : (
                <div className="w-full h-64 sm:h-80 md:h-96 bg-white rounded-lg shadow-sm border border-gray-200">
                  <iframe
                    src={previewUrl}
                    className="w-full h-full rounded-lg"
                    title="PDF Preview"
                  />
                </div>
              )}
            </div>
          ) : (
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Unable to preview this file</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
