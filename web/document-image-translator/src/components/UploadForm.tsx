"use client";
import React, { useRef, useState } from "react";
import type { UploadFormProps } from "@/types";

const UploadForm: React.FC<UploadFormProps> = ({ onUpload }) => {
  const [file, setFile] = useState<File | null>(null);
  const [targetLang, setTargetLang] = useState("");
  const [uploading, setUploading] = useState(false);

  const getPresignedUrl = async (fileName: string, targetLang: string) => {
    const res = await fetch(`/api/presigned-url?file_name=${encodeURIComponent(fileName)}&target_language=${encodeURIComponent(targetLang)}`);
    if (!res.ok) throw new Error("Failed to get presigned url");
    return res.json();
  };

  const uploadToS3 = async (url: string, file: File) => {
    const res = await fetch(url, {
      method: "PUT",
      body: file,
      headers: { "Content-Type": "application/octet-stream" },
    });
    if (!res.ok) throw new Error("Failed to upload to S3");
  };

  const recordUpload = async (uuid: string, fileName: string, targetLang: string) => {
    const res = await fetch("/api/upload-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uuid, file_name: fileName, target_language: targetLang }),
    });
    if (!res.ok) throw new Error("Failed to record upload");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !targetLang) return;
    setUploading(true);
    try {
      const { upload_url, uuid } = await getPresignedUrl(file.name, targetLang);
      await uploadToS3(upload_url, file);
      await recordUpload(uuid, file.name, targetLang);
      onUpload(uuid, file.name, targetLang);
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form className="flex flex-col gap-4 w-full max-w-md bg-white p-6 rounded shadow" onSubmit={handleSubmit}>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        required
      />
      <input
        type="text"
        placeholder="Target language (e.g. fr, de, es)"
        value={targetLang}
        onChange={(e) => setTargetLang(e.target.value)}
        required
      />
      <button
        type="submit"
        className="bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50"
        disabled={uploading}
      >
        {uploading ? "Uploading..." : "Upload & Translate"}
      </button>
    </form>
  );
};

export default UploadForm;
