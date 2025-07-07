import React from "react";
import LanguageSelectClient from "./LanguageSelectClient";

export default function LanguageSelect() {
  return (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Target Language
      </label>
      <LanguageSelectClient />
    </div>
  );
}
