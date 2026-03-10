import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "NIL Institute — College Athlete NIL Valuations",
  description: "The definitive source for predicted NIL valuations for college athletes, updated weekly.",
};

const clerkPubKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
const clerkEnabled = clerkPubKey && !clerkPubKey.startsWith("pk_replace");

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  if (clerkEnabled) {
    const { ClerkProvider } = await import("@clerk/nextjs");
    return (
      <ClerkProvider>
        <html lang="en" className={inter.variable}>
          <body>
            <Navbar />
            {children}
          </body>
        </html>
      </ClerkProvider>
    );
  }

  return (
    <html lang="en" className={inter.variable}>
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
