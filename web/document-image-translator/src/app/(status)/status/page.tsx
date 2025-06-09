'use client';
import React, { useState } from "react";
import StatusDisplay from "@/components/StatusDisplay";
import TranslationViewer from "@/components/TranslationViewer";
import type { Status } from "@/types";

export default function StatusPage() {
  const [uuid, setUuid] = useState("");
  const [fileName, setFileName] = useState("");
  const [status, setStatus] = useState<Status | null>(null);
  const [htmlContent, setHtmlContent] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    setHtmlContent("");
    try {
      const res = await fetch(`/api/status?uuid=${encodeURIComponent(uuid)}&file_name=${encodeURIComponent(fileName)}`);
      if (!res.ok) throw new Error("Status not found");
      const data = await res.json();
      setStatus(data);
      if (data.status === "complete" && data.html_url) {
        const html = await fetch(data.html_url).then((r) => r.text());
        setHtmlContent(html);
      }
    } catch (err) {
      setStatus({ status: "error", error: (err as Error).message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 gap-8 bg-gray-50">
      <h1 className="text-3xl font-bold mb-4 text-blue-900">Check Translation Status</h1>
      <form className="flex flex-col gap-4 w-full max-w-md bg-white p-6 rounded shadow" onSubmit={handleCheck}>
        <input
          type="text"
          placeholder="UUID"
          value={uuid}
          onChange={(e) => setUuid(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="File name (original)"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          required
        />
        <button
          type="submit"
          className="bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Checking..." : "Check Status"}
        </button>
      </form>
      <StatusDisplay status={status} />
      <TranslationViewer htmlContent={htmlContent} />
    </main>
  );
}
