import React from "react";
import type { TranslationViewerProps } from "@/types";

const TranslationViewer: React.FC<TranslationViewerProps> = ({ htmlContent }) => {
  if (!htmlContent) return null;
  return (
    <div className="mt-8 w-full max-w-2xl border rounded bg-white p-4 shadow">
      <h2 className="text-xl font-semibold mb-2">Translation Result</h2>
      <iframe
        srcDoc={htmlContent}
        title="Translation Result"
        className="w-full min-h-[400px] border"
      />
    </div>
  );
};

export default TranslationViewer;
