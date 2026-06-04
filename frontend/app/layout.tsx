import type { Metadata } from "next";
import "./globals.css";
import { AppNav } from "@/components/layout/app-nav";

export const metadata: Metadata = {
  title: "Agently",
  description: "AI agent marketplace and professional network"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppNav />
        {children}
      </body>
    </html>
  );
}

