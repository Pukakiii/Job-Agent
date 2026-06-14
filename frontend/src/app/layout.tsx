import type { Metadata } from "next"
import { Geist, Geist_Mono, Luxurious_Roman } from "next/font/google"

import AuthProvider from "@/features/auth/AuthProvider"
import MSWProvider  from "@/mocks/MSWProvider"
import "./globals.css"

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
})

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

const luxuriousRoman = Luxurious_Roman({
  weight: ["400"],
  subsets: ["latin"],
  variable: "--font-logo",
})

export const metadata: Metadata = {
  title: "Job Agent",
  description: "AI-powered job search platform",
}

export const viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en"
      className={`${geist.variable} ${geistMono.variable} ${luxuriousRoman.variable} antialiased`}
      style={{ WebkitTextSizeAdjust: "100%" }}
      suppressHydrationWarning
    >
      <body className="min-h-screen min-h-[100svh] min-h-[100dvh] bg-background text-foreground">
        <MSWProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </MSWProvider>
      </body>
    </html>
  )
}
