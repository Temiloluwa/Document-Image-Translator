import React from "react";
import { LANGUAGES } from "@/lib/constants";
import ImageTranslatorApp from "@/components/app/ImageTranslatorApp";

export default function Page() {
  const defaultLanguage = LANGUAGES[0].code;

  return (
    <div className="flex h-screen bg-gray-50">
      <ImageTranslatorApp
        initialLanguage={defaultLanguage}
        languages={LANGUAGES}
      />
    </div>
  );
}
