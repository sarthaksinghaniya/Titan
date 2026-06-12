import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: {
    default: "TITAN — Autonomous Governance Intelligence",
    template: "%s | TITAN",
  },
  description:
    "A production-grade multi-agent AI platform where AI ministers independently analyze, debate, vote, and simulate policy solutions for societal problems.",
  keywords: ["AI governance", "multi-agent", "policy simulation", "LangGraph", "Gemini"],
  authors: [{ name: "TITAN Team" }],
  robots: "index, follow",
  openGraph: {
    type: "website",
    siteName: "TITAN",
    title: "TITAN — Autonomous Governance Intelligence",
    description: "AI ministers debate, vote, and simulate solutions for societal problems.",
  },
};

export const viewport: Viewport = {
  themeColor: "#050508",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#13131f",
              border: "1px solid rgba(255,255,255,0.08)",
              color: "rgba(255,255,255,0.9)",
            },
          }}
        />
      </body>
    </html>
  );
}
