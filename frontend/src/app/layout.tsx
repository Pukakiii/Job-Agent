import type { Metadata } from "next"
import { Geist, Geist_Mono, Girassol } from "next/font/google"

import AuthProvider from "@/features/auth/AuthProvider"
import ThemeProvider from "@/features/theme/ThemeProvider"
import MSWProvider from "@/mocks/MSWProvider"
import "./globals.css"

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-sans",
})

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

const girassol = Girassol({
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
      className={`${geist.variable} ${geistMono.variable} ${girassol.variable} antialiased`}
      style={{ WebkitTextSizeAdjust: "100%" }}
      suppressHydrationWarning
    >
      <body className="min-h-screen min-h-[100svh] min-h-[100dvh] bg-background text-foreground">
        <MSWProvider>
          <ThemeProvider>
            <AuthProvider>{children}</AuthProvider>
          </ThemeProvider>
        </MSWProvider>
      </body>
    </html>
  )
}
