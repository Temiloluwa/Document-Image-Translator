import React from "react";
import LanguageSelect from "./LanguageSelect";
import FileUpload from "./FileUpload";
import SelectedFileInfo from "./SelectedFileInfo";
import StatusDisplay from "./StatusDisplay";
import UploadButton from "./UploadButton";

import ToggleInfoMessage from "./ToggleInfoMessage";



export default function Sidebar() {
  // Height of Navbar is p-2 sm:p-4 (py-2/py-4), so use min-h-[56px] (14*4) for consistency
  return (
    <div className="w-full md:w-80 bg-white border-b md:border-b-0 md:border-r border-gray-200 p-0 md:p-0 flex flex-col h-auto md:h-full items-start">
      {/* Top bar: same height as Navbar, center logo */}
      <div className="flex items-center justify-center w-full min-h-[64px] relative">
        <LogoWithText />
        {/* Hamburger/X button for mobile sidebar close */}
        <div className="md:hidden absolute right-4 top-1/2 -translate-y-1/2">
          {/* HamburgerButton will be conditionally rendered by parent, so nothing here */}
        </div>
      </div>
      <hr className="border-gray-200 w-full" style={{height: '1px'}} />
      <div className="flex flex-col flex-1 justify-center w-full px-4 md:px-6 pt-8">
        <div className="flex flex-col items-center gap-3 w-full mb-6">
          <div className="w-full flex justify-center">
            <LanguageSelect />
          </div>
          <FileUpload />
          <SelectedFileInfo />
        </div>
        <div className="flex flex-col items-start gap-3 w-full">
          <StatusDisplay />
          <UploadButton />
          <ToggleInfoMessage />
        </div>
      </div>
    </div>
  );
}

function LogoWithText() {
  return (
    <span className="flex items-center font-sans font-light text-xl tracking-tight text-blue-700 mx-auto md:mx-0 select-none" style={{ fontFamily: 'Inter, Arial, Helvetica, sans-serif' }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/logo.svg" alt="Logo" className="h-9 w-9 inline-block mr-1.5" />
      <span>ImageTranslator</span>
    </span>
  );
}
