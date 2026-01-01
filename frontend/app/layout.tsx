import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TravelGenie - AI Travel Planner",
  description: "Your intelligent multilingual travel companion for planning amazing trips worldwide",
  keywords: ["travel", "AI", "planner", "multilingual", "destinations", "itinerary"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased bg-(--color-background) text-(--color-text-primary) min-h-screen">
        {children}
      </body>
    </html>
  );
}
