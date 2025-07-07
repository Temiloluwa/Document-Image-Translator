


import React from "react";

import LanguageSelect from "./LanguageSelect";
import FileUpload from "./FileUpload";
import SelectedFileInfo from "./SelectedFileInfo";
import StatusDisplay from "./StatusDisplay";
import UploadButton from "./UploadButton";
import HamburgerButton from "@/components/app/HamburgerButton";

// Use the same logo as the desktop sidebar
function LogoWithText() {
  return (
    <span className="flex items-center font-sans font-light text-xl tracking-tight text-blue-700 mx-auto select-none" style={{ fontFamily: 'Inter, Arial, Helvetica, sans-serif' }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/logo.svg" alt="Logo" className="h-9 w-9 inline-block mr-1.5" />
      <span>ImageTranslator</span>
    </span>
  );
}

export default function SidebarContentOnly({ onClose }: { onClose?: () => void } = {}) {
  // The sidebar area is always white and visible; overlay is handled by parent
  return (
    <div className="relative flex flex-col flex-1 w-full h-full bg-white px-2 py-2 gap-2 overflow-y-auto max-h-[calc(100vh-4rem)]">
      {/* Logo and close button on the same line for mobile */}
      <div className="flex items-center justify-between w-full min-h-[64px] px-2">
        <LogoWithText />
        {onClose && (
          <HamburgerButton isOpen={true} onClick={onClose} />
        )}
      </div>
      <hr className="border-gray-200 w-full mb-2" style={{height: '1px'}} />
      <div className="flex flex-col gap-2 w-full">
        <div className="w-full flex justify-center">
          <LanguageSelect />
        </div>
        <FileUpload />
        <SelectedFileInfo />
      </div>
      <div className="flex flex-col gap-2 w-full">
        <StatusDisplay />
        <UploadButton />
      </div>
    </div>
  );
}
