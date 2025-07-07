"use client";

import React, { createContext, useContext, ReactNode } from "react";
import { useImageTranslator } from "@/hooks/useImageTranslator";

import type { UploadStatus } from "@/types";
import type { Language } from "@/lib/constants";

interface ImageTranslatorContextType {
  selectedFile: File | null;
  uploadStatus: UploadStatus;
  processingProgress: number;
  errorMessage: string;
  fileUuid: string | null;
  downloadUrl: string | null;
  targetLanguage: string;
  showTranslated: boolean;
  previewUrl: string | null;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  languages: readonly Language[];
  handleDrop: (e: React.DragEvent) => void;
  handleDragOver: (e: React.DragEvent) => void;
  handleFileInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleUpload: () => Promise<void>;
  handleReset: () => void;
  formatFileSize: (bytes: number) => string;
  canUpload: boolean;
  canToggle: boolean;
  isFileSelected: boolean;
  setTargetLanguage: (language: string) => void;
  setShowTranslated: (show: boolean) => void;
  translatedHtml: string | null;
}

const ImageTranslatorContext = createContext<ImageTranslatorContextType | undefined>(undefined);

interface ImageTranslatorProviderProps {
  children: ReactNode;
  initialLanguage: string;
  languages: readonly Language[];
}

export function ImageTranslatorProvider({
  children,
  initialLanguage,
  languages
}: ImageTranslatorProviderProps) {
  const translatorState = useImageTranslator();

  // Only set initial language on mount, not on every prop change
  React.useEffect(() => {
    // Only set on mount
    translatorState.setTargetLanguage(initialLanguage);
    // The empty dependency array is correct and will not cause the error
    // The error was likely due to a dynamic dependency array in a previous version
  }, []);

  const contextValue = {
    ...translatorState,
    languages,
    translatedHtml: translatorState.translatedHtml,
  };

  return (
    <ImageTranslatorContext.Provider value={contextValue}>
      {children}
    </ImageTranslatorContext.Provider>
  );
}

export function useImageTranslatorContext() {
  const context = useContext(ImageTranslatorContext);
  if (context === undefined) {
    throw new Error("useImageTranslatorContext must be used within an ImageTranslatorProvider");
  }
  return context;
}
