import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata = {
  title: "Cold Email AI | Premium Outreach Dashboard",
  description: "Generate highly personalized, AI-driven cold emails in seconds.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${outfit.variable} font-sans`}>{children}</body>
    </html>
  );
}
