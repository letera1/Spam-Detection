import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NexusML SpamGuard - AI Spam Detection",
  description: "Advanced spam detection system using machine learning to classify messages as spam or ham with detailed analysis.",
  icons: {
    icon: "https://cdn-icons-png.flaticon.com/512/2889/2889312.png", // Shield/Security icon
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
