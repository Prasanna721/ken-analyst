import type { Metadata } from "next";
import { instrumentSerif, monument } from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ken Analyst",
  description: "Financial analysis platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${monument.variable} ${instrumentSerif.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
