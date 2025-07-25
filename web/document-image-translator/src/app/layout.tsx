import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

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
    <html lang="en" className="h-full min-h-screen">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased h-full min-h-screen`}>
        <div className="flex flex-col h-full min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
