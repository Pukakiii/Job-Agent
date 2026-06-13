"use client"

import Link from "next/link"
import type { ComponentType } from "react"
import { usePathname } from "next/navigation"
import {
  Briefcase,
  FileText,
  FolderKanban,
  LayoutDashboard,
  Mail,
  Settings,
  Upload,
} from "lucide-react"

import { cn } from "@/lib/utils"

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/jobs", label: "Jobs", icon: Briefcase },
  { href: "/dashboard/cvs", label: "CVs", icon: Upload },
  { href: "/dashboard/applications", label: "Applications", icon: FolderKanban },
  { href: "/dashboard/documents", label: "Documents", icon: FileText },
  { href: "/dashboard/outreach", label: "Outreach", icon: Mail },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
] as const

function NavLink({
  href,
  label,
  icon: Icon,
  exact,
}: {
  href: string
  label: string
  icon: ComponentType<{ className?: string }>
  exact?: boolean
}) {
  const pathname = usePathname()
  const isActive = exact ? pathname === href : pathname.startsWith(href)

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
        isActive
          ? "border-l-2 border-[var(--color-accent-border)] bg-[var(--color-accent-subtle)] pl-[10px] text-[var(--color-accent-hover)]"
          : "text-muted-foreground hover:text-foreground",
      )}
    >
      <Icon className="size-4 shrink-0" />
      {label}
    </Link>
  )
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-[100dvh] bg-background">
      <aside className="flex w-[220px] shrink-0 flex-col border-r border-border bg-sidebar">
        <div className="border-b border-border px-5 py-5">
          <span className="font-logo text-lg text-foreground">Job Agent</span>
        </div>
        <nav className="flex flex-1 flex-col gap-1 p-3">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.href} {...item} />
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  )
}
