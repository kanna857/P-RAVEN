import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAVEN — Responsible Audio Verification & Evidence Navigator",
  description: "Multilingual voice intelligence and evidence investigation platform powered by Gnani AI Prisma and Timbre.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#101B2B] text-[#F6F5F1] antialiased">
        {children}
      </body>
    </html>
  );
}
