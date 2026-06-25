"use client"

import { usePathname } from "next/navigation"

import { ThemeToggle } from "@/components/theme/theme-toggle"

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Overview",
  "/dashboard/jobs": "Jobs",
  "/dashboard/cvs": "CVs",
  "/dashboard/applications": "Applications",
  "/dashboard/documents": "Documents",
  "/dashboard/outreach": "Outreach",
  "/dashboard/settings": "Settings",
}

function getPageTitle(pathname: string): string {
  if (PAGE_TITLES[pathname]) {
    return PAGE_TITLES[pathname]
  }

  const match = Object.keys(PAGE_TITLES)
    .filter((href) => href !== "/dashboard")
    .sort((a, b) => b.length - a.length)
    .find((href) => pathname.startsWith(`${href}/`))

  return match ? PAGE_TITLES[match] : "Dashboard"
}

export function DashboardHeader({
  leading,
}: {
  leading?: React.ReactNode
}) {
  const pathname = usePathname()
  const title = getPageTitle(pathname)

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4 sm:px-6">
      <div className="flex min-w-0 items-center gap-2">
        {leading}
        <h1 className="truncate text-lg font-semibold tracking-tight text-foreground">
          {title}
        </h1>
      </div>
      <ThemeToggle />
    </header>
  )
}
