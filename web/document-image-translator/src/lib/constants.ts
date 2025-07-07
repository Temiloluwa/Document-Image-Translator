export const LANGUAGES = [
  { code: "english", name: "English" },
  { code: "chinese", name: "Chinese" },
  { code: "portuguese", name: "Portuguese" },
  { code: "german", name: "German" },
  { code: "italian", name: "Italian" },
  { code: "spanish", name: "Spanish" },
  { code: "french", name: "French" },
  { code: "arabic", name: "Arabic" },
  { code: "hindi", name: "Hindi" },
  { code: "bengali", name: "Bengali" },
  { code: "russian", name: "Russian" },
  { code: "indonesian", name: "Indonesian" },
  { code: "japanese", name: "Japanese" },
  { code: "swahili", name: "Swahili" },
  { code: "marathi", name: "Marathi" },
  { code: "telugu", name: "Telugu" },
  { code: "turkish", name: "Turkish" },
  { code: "tamil", name: "Tamil" },
  { code: "vietnamese", name: "Vietnamese" },
  { code: "korean", name: "Korean" },
  { code: "thai", name: "Thai" },

  { code: "gujarati", name: "Gujarati" },
  { code: "polish", name: "Polish" }
] as const;

export type Language = typeof LANGUAGES[number];

export const FILE_CONSTRAINTS = {
  maxSize: 10 * 1024 * 1024, // 10MB
  allowedTypes: ["image/jpeg", "image/png", "image/webp", "application/pdf"],
  allowedExtensions: [".jpg", ".jpeg", ".png", ".webp", ".pdf"],
} as const;

export const UPLOAD_STATUS = {
  IDLE: "idle",
  UPLOADING: "uploading",
  PROCESSING: "processing",
  COMPLETED: "completed",
  ERROR: "error",
} as const;
