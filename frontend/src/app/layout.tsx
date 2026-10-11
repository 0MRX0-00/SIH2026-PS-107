import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/AppShell";
import { LanguageProvider } from "@/context/LanguageContext";

export const metadata: Metadata = {
  title: "e-BIS Sahayak | Indian Standards & BIS Information Assistant",
  description:
    "Official AI Assistant for Indian Standards (IS), mandatory Quality Control Orders (QCOs), certification schemes (ISI Mark, CRS, FMCS), and accredited laboratory testing facilities.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#F8FAFC] text-[#0F172A] min-h-screen antialiased">
        <LanguageProvider>
          <AppShell>{children}</AppShell>
        </LanguageProvider>
      </body>
    </html>
  );
}
