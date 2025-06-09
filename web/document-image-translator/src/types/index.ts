// Central types for the Document Image Translator frontend

export interface Status {
  status?: string;
  updated_at?: string;
  error?: string;
  html_url?: string;
  [key: string]: any;
}

export interface UploadFormProps {
  onUpload: (uuid: string, fileName: string, targetLang: string) => void;
}

export interface StatusDisplayProps {
  status: Status | null;
}

export interface TranslationViewerProps {
  htmlContent: string;
}
