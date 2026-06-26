import type { Metadata } from "next"
import { Geist, Geist_Mono, Girassol } from "next/font/google"
import { ThemeProvider } from "@teispace/next-themes"
import { getTheme, getThemeScript } from "@teispace/next-themes/server"

import AuthProvider from "@/features/auth/AuthProvider"
import {
  buildThemeScriptOptions,
  themeConfig,
  themeServerOptions,
} from "@/lib/theme-config"
import { Toaster } from "sonner"
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

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const initialTheme = await getTheme(themeServerOptions)
  const themeScript = getThemeScript(buildThemeScriptOptions(initialTheme))

  return (
    <html
      lang="en"
      className={`${geist.variable} ${geistMono.variable} ${girassol.variable} antialiased`}
      style={{ WebkitTextSizeAdjust: "100%" }}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-screen min-h-[100svh] min-h-[100dvh] bg-background text-foreground">
        <ThemeProvider
          {...themeConfig}
          initialTheme={initialTheme ?? undefined}
          noScript
        >
          <AuthProvider>
            {children}
            <Toaster richColors closeButton position="top-right" />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
