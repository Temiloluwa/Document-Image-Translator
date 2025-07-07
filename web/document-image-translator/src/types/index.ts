
// Use string literal types to avoid import type issues
export type Language =
  | { code: "spanish"; name: "Spanish" }
  | { code: "french"; name: "French" }
  | { code: "german"; name: "German" }
  | { code: "italian"; name: "Italian" }
  | { code: "portuguese"; name: "Portuguese" }
  | { code: "chinese"; name: "Chinese" }
  | { code: "japanese"; name: "Japanese" }
  | { code: "korean"; name: "Korean" };

export type UploadStatus =
  | "idle"
  | "uploading"
  | "processing"
  | "completed"
  | "error";

export interface FileInfo {
  file: File;
  uuid: string | null;
  previewUrl: string | null;
}

export interface TranslationState {
  selectedFile: File | null;
  uploadStatus: UploadStatus;
  processingProgress: number;
  errorMessage: string;
  fileUuid: string | null;
  downloadUrl: string | null;
  targetLanguage: string;
  showTranslated: boolean;
  previewUrl: string | null;
}
