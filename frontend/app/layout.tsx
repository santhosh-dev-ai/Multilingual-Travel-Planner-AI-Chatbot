import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TravelGenie - Student Trip Planner",
  description:
    "TravelGenie helps students plan affordable, efficient, and memorable trips. Get personalized, budget-friendly itineraries using AI, maps, and real-time data—perfect for students with limited budgets!",
  keywords: [
    "travel",
    "AI",
    "planner",
    "student",
    "budget",
    "multilingual",
    "destinations",
    "itinerary",
    "personalized",
    "maps",
    "location data",
    "affordable"
  ],
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
