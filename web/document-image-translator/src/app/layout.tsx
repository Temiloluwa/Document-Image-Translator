import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Document Image Translator",
  description: "Translate document images to your target language and visualize the result.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <nav className="w-full flex justify-center gap-8 py-4 bg-white shadow-sm mb-4">
          <Link href="/" className="font-semibold text-blue-900 hover:underline">Home</Link>
          <Link href="/upload" className="font-semibold text-blue-900 hover:underline">Upload</Link>
          <Link href="/status" className="font-semibold text-blue-900 hover:underline">Status</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
