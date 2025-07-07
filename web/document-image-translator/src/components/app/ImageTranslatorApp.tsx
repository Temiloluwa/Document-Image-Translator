"use client";

import React from "react";
import { ImageTranslatorProvider } from "@/providers/ImageTranslatorProvider";
import Sidebar from "@/components/app/sidebar/Sidebar";
import SidebarContentOnly from "@/components/app/sidebar/SidebarContentOnly";
// import HamburgerButton from "@/components/app/HamburgerButton";
import MainArea from "@/modules/app/main-area";
import { Language } from "@/lib/constants";

interface ImageTranslatorAppProps {
  initialLanguage: string;
  languages: readonly Language[];
}

export default function ImageTranslatorApp(props: ImageTranslatorAppProps) {
  const { initialLanguage, languages } = props;
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  // Close sidebar on route change or language change (optional, not implemented here)

  React.useEffect(() => {
    const handler = () => setSidebarOpen(true);
    window.addEventListener('openSidebar', handler);
    return () => window.removeEventListener('openSidebar', handler);
  }, []);

  return (
    <ImageTranslatorProvider
      initialLanguage={initialLanguage}
      languages={languages}
    >
      <div className="flex flex-col md:flex-row min-h-screen w-full h-full bg-gray-50 fixed top-0 left-0 inset-0">
        {/* Sidebar overlay for mobile */}
        <div
          className={`fixed inset-0 bg-white/30 z-20 transition-opacity duration-200 md:hidden ${sidebarOpen ? 'block' : 'hidden'}`}
          onClick={() => setSidebarOpen(false)}
        />
        {/* Sidebar itself */}
        <aside
          className={`fixed z-30 top-0 left-0 h-full w-4/5 max-w-xs md:static md:w-80 md:max-w-none md:block bg-white border-r border-gray-200 transition-transform duration-200 transform md:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative`}
          style={{ boxShadow: sidebarOpen ? '0 0 0 9999px rgba(0,0,0,0.4)' : undefined }}
        >
          {/* Mobile: show header and sidebar content only when open; Desktop: always show sidebar */}
          {sidebarOpen ? (
            <>
              <SidebarContentOnly onClose={() => setSidebarOpen(false)} />
            </>
          ) : (
            <div className="hidden md:block">
              <Sidebar />
            </div>
          )}
        </aside>
        {/* Main content */}
        <div className="flex-1 flex flex-col w-full md:w-auto">
          <MainArea />
        </div>
      </div>
    </ImageTranslatorProvider>
  );
}
