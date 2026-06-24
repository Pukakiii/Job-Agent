"use client"

import { useState } from "react"
import { Menu, X } from "lucide-react"

import { SidebarBrand } from "@/components/brand/sidebar-brand"
import { DashboardHeader } from "@/components/layout/dashboard-header"
import { SidebarFooter } from "@/components/layout/sidebar-footer"
import { SidebarNav } from "@/components/layout/sidebar-nav"
import { Button } from "@/components/ui/button"

type DashboardShellProps = {
  children: React.ReactNode
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <>
      <SidebarBrand />
      <SidebarNav onNavigate={onNavigate} />
      <SidebarFooter />
    </>
  )
}

export function DashboardShell({ children }: DashboardShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex h-dvh overflow-hidden bg-background">
      <aside className="hidden h-full w-[220px] shrink-0 flex-col border-r border-border bg-sidebar lg:flex">
        <SidebarContent />
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            aria-label="Close navigation"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative flex h-full w-[min(280px,85vw)] flex-col border-r border-border bg-sidebar shadow-lg">
            <div className="flex items-center justify-end border-b border-border p-2">
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                onClick={() => setMobileOpen(false)}
                aria-label="Close menu"
              >
                <X className="size-4" />
              </Button>
            </div>
            <SidebarContent onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      ) : null}

      <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-auto">
        <DashboardHeader
          leading={
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className="lg:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open navigation menu"
            >
              <Menu className="size-4" />
            </Button>
          }
        />
        {children}
      </main>
    </div>
  )
}
