import React from "react";

export default function HamburgerButton({ onClick, isOpen }: { onClick: () => void; isOpen: boolean }) {
  return (
    <button
      className="md:hidden p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
      onClick={onClick}
      type="button"
    >
      <span className="sr-only">{isOpen ? "Close sidebar" : "Open sidebar"}</span>
      <svg
        className="w-7 h-7 text-gray-700"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        {isOpen ? (
          // X icon
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        ) : (
          // Hamburger icon
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        )}
      </svg>
    </button>
  );
}
