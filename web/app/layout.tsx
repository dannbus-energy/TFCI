import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TFCI - Transition Finance Credibility Index",
  description: "Measuring execution capacity, not announced intent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
