"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { LogOut, Settings } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useAuthContext } from "@/features/auth/AuthProvider"
import { cn } from "@/lib/utils"

const SETTINGS_HREF = "/dashboard/settings"

function isSettingsActive(pathname: string): boolean {
  return (
    pathname === SETTINGS_HREF || pathname.startsWith(`${SETTINGS_HREF}/`)
  )
}

export function SidebarFooter() {
  const pathname = usePathname()
  const router = useRouter()
  const { logout } = useAuthContext()
  const settingsActive = isSettingsActive(pathname)

  async function handleLogout() {
    await logout()
    router.push("/login")
  }

  return (
    <div className="mt-auto border-t border-border px-2 py-3">
      <Link
        href={SETTINGS_HREF}
        className={cn(
          "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
          settingsActive
            ? "border-l-2 border-[var(--primary)] bg-[var(--color-accent-subtle)] text-[var(--primary)]"
            : "text-muted-foreground hover:bg-[var(--color-surface-hover)] hover:text-foreground",
        )}
      >
        <Settings className="size-4 shrink-0" aria-hidden />
        Settings
      </Link>
      <Button
        type="button"
        variant="ghost"
        className="mt-1 w-full justify-start gap-3 px-3 text-sm font-medium text-muted-foreground hover:bg-[var(--color-surface-hover)] hover:text-foreground"
        onClick={() => {
          void handleLogout()
        }}
      >
        <LogOut className="size-4 shrink-0" aria-hidden />
        Logout
      </Button>
    </div>
  )
}
