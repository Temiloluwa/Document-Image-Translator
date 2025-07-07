export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

export function validateFile(file: File) {
  const maxFileSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = ["image/jpeg", "image/png", "image/webp", "application/pdf"];

  if (!file) return { valid: false, error: "No file selected" };

  if (file.size > maxFileSize) {
    return { valid: false, error: "File size too large. Maximum size is 10MB." };
  }

  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: "Invalid file type. Please upload an image (JPEG, PNG, WebP) or PDF." };
  }

  return { valid: true };
}
