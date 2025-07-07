"use client"
import { useState, useCallback, useRef } from "react";
// pollStatus removed, logic is now in pollStatusHandler

export function useImageTranslator() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "processing" | "completed" | "error">("idle");
  const [processingProgress, setProcessingProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [fileUuid, setFileUuid] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [targetLanguage, setTargetLanguage] = useState("spanish");
  const [showTranslated, setShowTranslated] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const languages = [
    { code: "spanish", name: "Spanish" },
    { code: "french", name: "French" },
    { code: "german", name: "German" },
    { code: "italian", name: "Italian" },
    { code: "portuguese", name: "Portuguese" },
    { code: "chinese", name: "Chinese" },
    { code: "japanese", name: "Japanese" },
    { code: "korean", name: "Korean" },
  ];


  const maxFileSize = 10 * 1024 * 1024; // 10MB

  const handleFileSelect = useCallback((file: File) => {
    const allowedTypes = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
    const validateFile = (file: File) => {
      if (!file) return { valid: false, error: "No file selected" };
      if (file.size > maxFileSize) {
        return { valid: false, error: "File size too large. Maximum size is 10MB." };
      }
      if (!allowedTypes.includes(file.type)) {
        return { valid: false, error: "Invalid file type. Please upload an image (JPEG, PNG, WebP) or PDF." };
      }
      return { valid: true };
    };
    const validation = validateFile(file);
    if (!validation.valid) {
      setErrorMessage(validation.error!);
      setUploadStatus("error");
      return;
    }
    setSelectedFile(file);
    setUploadStatus("idle");
    setErrorMessage("");
    setProcessingProgress(0);
    setDownloadUrl(null);
    setShowTranslated(false);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  }, [maxFileSize, setErrorMessage, setUploadStatus, setSelectedFile, setProcessingProgress, setDownloadUrl, setShowTranslated, setPreviewUrl]);

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

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const getPresignedUrl = async (filename: string, targetLanguage: string) => {
    const response = await fetch(`/api/v1/presigned-url?filename=${encodeURIComponent(filename)}&target_language=${encodeURIComponent(targetLanguage)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  };

  const uploadFileToS3 = async (file: File, uploadUrl: string) => {
    const response = await fetch(uploadUrl, {
      method: "PUT",
      body: file,
      headers: {
        "Content-Type": file.type,
      },
    });
    if (!response.ok) {
      throw new Error(`Upload failed! status: ${response.status}`);
    }
    return true;
  };

  // Removed unused checkProcessingStatus

  // Polling logic using new API structure (result location)
  const pollStatusHandler = async (resultLocation: string) => {
    let retries = 0;
    const maxRetries = 3;
    const retryDelay = 5000;
    let stopped = false;

    const poll = async () => {
      if (stopped) return;
      try {
        const response = await fetch(`/api/v1/status?${resultLocation.endsWith('.html') ? 'html_results_location' : 'markdown_results_location'}=${encodeURIComponent(resultLocation)}`);
        if (response.ok) {
          const status = await response.json();
          if (status.markdown_results_location || status.html_results_location) {
            setUploadStatus("completed");
            setDownloadUrl(status.html_results_location || status.markdown_results_location);
            setProcessingProgress(100);
            stopped = true;
          } else if (status.status && status.status === "processing") {
            setProcessingProgress(status.progress || 0);
            setTimeout(poll, 2000);
          } else if (status.status && status.status === "error") {
            setUploadStatus("error");
            setErrorMessage(status.error || "Processing failed");
            stopped = true;
          } else {
            setUploadStatus("error");
            setErrorMessage("Unknown processing status");
            stopped = true;
          }
          retries = 0; // reset retries on any valid response
        } else {
          const text = await response.text();
          if ((response.status === 404 || text.toLowerCase().includes("item not found")) && retries < maxRetries) {
            retries++;
            setTimeout(poll, retryDelay);
            return;
          } else {
            setUploadStatus("error");
            setErrorMessage(text || `HTTP error: ${response.status}`);
            stopped = true;
          }
        }
      } catch (err) {
        let message = "";
        if (err instanceof Error) {
          message = err.message;
        } else if (typeof err === "string") {
          message = err;
        } else if (typeof err === "object" && err && "message" in err) {
          message = String((err as { message?: unknown }).message);
        }
        setUploadStatus("error");
        setErrorMessage(message || "Failed to check processing status");
        stopped = true;
      }
    };
    poll();
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      setUploadStatus("uploading");
      setErrorMessage("");
      const { upload_url, markdown_results_location, html_results_location } = await getPresignedUrl(selectedFile.name, targetLanguage);
      await uploadFileToS3(selectedFile, upload_url);
      setUploadStatus("processing");
      setProcessingProgress(0);
      // Prefer polling on html result location if available
      pollStatusHandler(html_results_location || markdown_results_location);
    } catch (error) {
      let message = "";
      if (error instanceof Error) {
        message = error.message;
      } else if (typeof error === "string") {
        message = error;
      } else if (typeof error === "object" && error && "message" in error) {
        message = String((error as { message?: unknown }).message);
      }
      setUploadStatus("error");
      setErrorMessage(message || "Upload failed");
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

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
    languages,
    handleDrop,
    handleDragOver,
    handleFileInputChange,
    handleUpload,
    formatFileSize,
    canUpload: selectedFile !== null && uploadStatus === "idle",
    canToggle: uploadStatus === "completed" && !!downloadUrl,
    isFileSelected: selectedFile !== null,
  };
}
