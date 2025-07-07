"use client"
import React from "react";
import LanguageSelect from "@/components/app/sidebar/LanguageSelect";
import FileUpload from "@/components/app/sidebar/FileUpload";
import SelectedFileInfo from "@/components/app/sidebar/SelectedFileInfo";
import StatusDisplay from "@/components/app/sidebar/StatusDisplay";
import UploadButton from "@/components/app/sidebar/UploadButton";

interface SidebarProps {
  title: string;
  description: string;
}

export default function Sidebar({ title, description }: SidebarProps) {
  return (
    <div className="w-80 bg-white border-r border-gray-200 p-6 flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
        <p className="text-gray-600">{description}</p>
      </div>
      <LanguageSelect />
      <FileUpload />
      <SelectedFileInfo />
      <StatusDisplay />
      <UploadButton />
    </div>
  );
}
