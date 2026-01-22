import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Task Management System",
  description: "Manage your tasks efficiently with our Task Management System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#0B0F19] text-slate-50 min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
