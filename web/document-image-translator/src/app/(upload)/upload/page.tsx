'use client';

import UploadForm from "@/components/UploadForm";
import StatusDisplay from "@/components/StatusDisplay";
import TranslationViewer from "@/components/TranslationViewer";
import React, { useState, useRef, useEffect } from "react";
import { pollStatus } from "@/modules/pollStatus";
import type { Status } from "@/types";

export default function UploadPage() {
  const [status, setStatus] = useState<Status | null>(null);
  const [uuid, setUuid] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [htmlContent, setHtmlContent] = useState<string>("");
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const handleUpload = async (uuid: string, fileName: string, targetLang: string) => {
    setUuid(uuid);
    setFileName(fileName);
    setStatus({ status: "processing" });
    setHtmlContent("");
    pollingRef.current = pollStatus(uuid, fileName, (data: Status) => {
      setStatus(data);
      if (data.status === "complete" && data.html_url) {
        clearInterval(pollingRef.current!);
        fetch(data.html_url)
          .then((r) => r.text())
          .then(setHtmlContent);
      }
    });
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 gap-8 bg-gray-50">
      <h1 className="text-3xl font-bold mb-4 text-blue-900">Upload & Translate</h1>
      <UploadForm onUpload={handleUpload} />
      <StatusDisplay status={status} />
      <TranslationViewer htmlContent={htmlContent} />
    </main>
  );
}
