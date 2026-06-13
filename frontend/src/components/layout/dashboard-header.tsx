"use client"

import { usePathname } from "next/navigation"

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

export function DashboardHeader() {
  const pathname = usePathname()
  const title = getPageTitle(pathname)

  return (
    <header className="flex h-14 shrink-0 items-center border-b border-border px-6">
      <h1 className="text-lg font-semibold tracking-tight text-foreground">
        {title}
      </h1>
    </header>
  )
}
