"use client";

import { useState, useCallback, useRef } from "react";
import { LANGUAGES, UPLOAD_STATUS } from "@/lib/constants";
import { validateFile, formatFileSize } from "@/lib/utils";
import { getPresignedUrl, uploadFileToS3, checkProcessingStatus } from "@/lib/api";
import type { UploadStatus } from "@/types";

export function useImageTranslator() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>(UPLOAD_STATUS.IDLE);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [fileUuid, setFileUuid] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [targetLanguage, setTargetLanguageState] = useState<string>(LANGUAGES[0].code);
  // Store the fetched translated HTML
  const [translatedHtml, setTranslatedHtml] = useState<string | null>(null);
  // Fetch translated HTML from presigned URL with retry on 404
  const fetchTranslatedHtml = useCallback(async (url: string, retries = 3, delay = 2000) => {
    let attempt = 0;
    while (attempt < retries) {
      try {
        const response = await fetch(url);
        if (response.status === 404) {
          attempt++;
          if (attempt < retries) {
            await new Promise(res => setTimeout(res, delay));
            continue;
          } else {
            const error = new Error("Translated HTML not found (404)");
            console.error(error);
            throw error;
          }
        }
        if (!response.ok) {
          const error = new Error("Failed to fetch translated HTML");
          console.error(error);
          throw error;
        }
        const html = await response.text();
        setTranslatedHtml(html);
        return;
      } catch (err) {
        console.error('Error fetching translated HTML:', err);
        if (attempt < retries - 1) {
          attempt++;
          await new Promise(res => setTimeout(res, delay));
        } else {
          setErrorMessage("Could not load translated HTML");
          setTranslatedHtml(null);
          return;
        }
      }
    }
  }, []);

  const setTargetLanguage = (lang: string) => {
    setTargetLanguageState(lang);
  };
  const [showTranslated, setShowTranslated] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileSelect = useCallback((file: File) => {
    const validation = validateFile(file);
    if (!validation.valid) {
      setErrorMessage(validation.error!);
      setUploadStatus(UPLOAD_STATUS.ERROR);
      return;
    }
    setSelectedFile(file);
    setUploadStatus(UPLOAD_STATUS.IDLE);
    setErrorMessage("");
    setProcessingProgress(0);
    setDownloadUrl(null);
    setShowTranslated(false);
    // Clean up previous preview URL
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  }, [previewUrl]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // Enhanced polling with retry on 404/Item not found
  // Enhanced polling with retry on 404/Item not found, up to 3 times, 5s interval
  // Polling logic for new API: expects a result location string
  const pollStatusHandler = useCallback(
    async (resultLocation: string) => {
      let retries = 0;
      const maxRetries = 3;
      const retryDelay = 10000;

      const poll = async () => {
        try {
          const response = await checkProcessingStatus(resultLocation);
          // If processing is complete, API always returns html_results_url (presigned S3 URL)
          const htmlUrl = response.html_results_url;
          if (htmlUrl) {
            setUploadStatus(UPLOAD_STATUS.COMPLETED);
            setProcessingProgress(100);
            setDownloadUrl(htmlUrl);
            fetchTranslatedHtml(htmlUrl);
            return;
          }

          let progress: number = 0;
          let message: string = "";
          if (typeof response.status === "object" && response.status !== null) {
            if (typeof response.status.progress === "number") {
              progress = response.status.progress;
            }
            if (typeof response.status.message === "string") {
              message = response.status.message;
            }
          } else {
            if (typeof response.progress === "number") {
              progress = response.progress;
            }
            if (typeof response.message === "string") {
              message = response.message;
            }
          }

          setProcessingProgress(progress);
          if (progress < 100) {
            setUploadStatus(UPLOAD_STATUS.PROCESSING);
            setTimeout(poll, 2000);
          } else if (response.error) {
            setUploadStatus(UPLOAD_STATUS.ERROR);
            setErrorMessage(response.error || message || "Processing failed");
          } else {
            setUploadStatus(UPLOAD_STATUS.PROCESSING);
            setTimeout(poll, 2000);
          }
        } catch (error) {
          // Retry on 404/Item not found, up to 3 times, then show error
          let message = "";
          if (error instanceof Error) {
            message = error.message;
          } else if (typeof error === "string") {
            message = error;
          } else if (typeof error === "object" && error && "message" in error) {
            message = String((error as { message?: unknown }).message);
          }
          if (
            retries < maxRetries &&
            (message?.includes("404") || message?.toLowerCase().includes("item not found"))
          ) {
            retries++;
            setTimeout(poll, retryDelay);
          } else {
            setUploadStatus(UPLOAD_STATUS.ERROR);
            setErrorMessage(message || "Failed to check processing status");
          }
        }
      };
      poll();
    },
    [fetchTranslatedHtml]
  );

  const handleUpload = useCallback(async () => {
    if (!selectedFile) return;
    try {
      setUploadStatus(UPLOAD_STATUS.UPLOADING);
      setErrorMessage("");
      const { upload_url, markdown_results_location, html_results_location } = await getPresignedUrl(selectedFile.name, targetLanguage);
      // Use the markdown_results_location or html_results_location for polling
      const resultLocation = html_results_location || markdown_results_location;
      if (!resultLocation) throw new Error("No result location returned from API");
      await uploadFileToS3(selectedFile, upload_url);
      setUploadStatus(UPLOAD_STATUS.PROCESSING);
      setProcessingProgress(0);
      pollStatusHandler(resultLocation);
    } catch (error) {
      let message = "";
      if (error instanceof Error) {
        message = error.message;
      } else if (typeof error === "string") {
        message = error;
      } else if (typeof error === "object" && error && "message" in error) {
        message = String((error as { message?: unknown }).message);
      }
      setUploadStatus(UPLOAD_STATUS.ERROR);
      setErrorMessage(message || "Upload failed");
    }
  }, [selectedFile, targetLanguage, pollStatusHandler]);

  // Reset function for retry/reupload
  const handleReset = useCallback(() => {
    setSelectedFile(null);
    setUploadStatus(UPLOAD_STATUS.IDLE);
    setProcessingProgress(0);
    setErrorMessage("");
    setFileUuid(null);
    setDownloadUrl(null);
    setShowTranslated(false);
    setTranslatedHtml(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, [previewUrl]);

  return {
    selectedFile,
    setSelectedFile,
    uploadStatus,
    setUploadStatus,
    processingProgress,
    setProcessingProgress,
    errorMessage,
    setErrorMessage,
    fileUuid,
    setFileUuid,
    downloadUrl,
    setDownloadUrl,
    targetLanguage,
    setTargetLanguage,
    showTranslated,
    setShowTranslated,
    previewUrl,
    setPreviewUrl,
    fileInputRef,
    languages: LANGUAGES,
    handleDrop,
    handleDragOver,
    handleFileInputChange,
    handleUpload,
    handleReset,
    formatFileSize,
    canUpload: selectedFile !== null && uploadStatus === UPLOAD_STATUS.IDLE,
    canToggle: uploadStatus === UPLOAD_STATUS.COMPLETED && !!downloadUrl,
    isFileSelected: selectedFile !== null,
    translatedHtml,
  };
}
