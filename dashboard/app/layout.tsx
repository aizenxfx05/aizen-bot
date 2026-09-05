/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀█░▀█▀░▀▀█░█▀▀░█▀█   ░█░█░█▀▀░█░█                         ║
 * ║   ░█▀█░░█░░▄▀░░█▀▀░█░█   ░▄▀▄░█▀▀░▄▀▄                         ║
 * ║   ░▀░▀░▀▀▀░█▄▄░▀▀▀░▀░▀   ░▀░▀░▀░░░▀░▀                         ║
 * ║                                                                  ║
 * ║           © 2026 Aizen XFX — All Rights Reserved                ║
 * ║                                                                  ║
 * ║   discord  ──  https://discord.gg/M8qJ9W7vBb                    ║
 * ║   youtube  ──  https://youtube.com/@aizen_xfx                   ║
 * ║   github   ──  https://github.com/aizenxfx05                    ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/components/auth-provider";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

const brandName = process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX";

export const metadata: Metadata = {
  title: `${brandName} — Ultimate Discord Security Bot`,
  description: `${brandName} — Advanced Discord community management, AI chat, and military-grade server security.`,
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
      <body className="font-sans antialiased text-[#F3E8FF] bg-[#07070D]">
        <AuthProvider>
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  );
}
