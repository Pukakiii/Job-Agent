"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Briefcase,
  FileOutput,
  FileText,
  Kanban,
  LayoutDashboard,
  Mail,
  type LucideIcon,
} from "lucide-react"

import { cn } from "@/lib/utils"

type NavItem = {
  href: string
  label: string
  icon: LucideIcon
}

const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Overview" },
  { href: "/dashboard/jobs", icon: Briefcase, label: "Jobs" },
  { href: "/dashboard/cvs", icon: FileText, label: "CVs" },
  { href: "/dashboard/applications", icon: Kanban, label: "Applications" },
  { href: "/dashboard/documents", icon: FileOutput, label: "Documents" },
  { href: "/dashboard/outreach", icon: Mail, label: "Outreach" },
]

function isActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") {
    return pathname === "/dashboard"
  }

  return pathname === href || pathname.startsWith(`${href}/`)
}

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname()

  return (
    <nav className="flex-1 min-h-0 overflow-y-auto py-4">
      <ul className="flex flex-col gap-0.5 px-2">
        {NAV_ITEMS.map((item) => {
          const active = isActive(pathname, item.href)
          const Icon = item.icon

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "border-l-2 border-[var(--primary)] bg-[var(--color-accent-subtle)] text-[var(--primary)]"
                    : "text-muted-foreground hover:bg-[var(--color-surface-hover)] hover:text-foreground",
                )}
              >
                <Icon className="size-4 shrink-0" aria-hidden />
                {item.label}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
