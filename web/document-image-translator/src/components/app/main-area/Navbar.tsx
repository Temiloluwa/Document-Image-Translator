import React from "react";
import PreviewToggle from "./PreviewToggle";
import HamburgerButton from "@/components/app/HamburgerButton";

export default function Navbar() {
  // Hamburger open handler will be passed as a prop in a real app, but for now use a custom event
  const handleHamburger = () => {
    const event = new CustomEvent('openSidebar');
    window.dispatchEvent(event);
  };
  return (
    <nav className="w-full bg-white border-b border-gray-200 p-2 sm:p-4 flex items-center shadow-sm relative">
      {/* Hamburger for mobile */}
      <div className="md:hidden flex items-center">
        <HamburgerButton isOpen={false} onClick={handleHamburger} />
      </div>
      <div className="flex-1 flex justify-center">
        <h2 className="text-lg sm:text-xl md:text-2xl font-light tracking-tight text-blue-700 font-sans text-center select-none" style={{ fontFamily: 'Inter, Arial, Helvetica, sans-serif' }}>
          Document Preview
        </h2>
      </div>
      <div className="absolute right-2 sm:right-6">
        <PreviewToggle />
      </div>
    </nav>
  );
}
