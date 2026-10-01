import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ORBIT | Autonomous Data Operations Control Tower",
  description: "Next-generation self-healing data platform. Real-time 3D Data Galaxy, autonomous multi-agent incident diagnosis, chaos engineering, and operational intelligence.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground font-sans min-h-screen bg-grain">
        {children}
      </body>
    </html>
  );
}
