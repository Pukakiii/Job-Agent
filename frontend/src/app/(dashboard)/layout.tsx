import { SidebarBrand } from "@/components/brand/sidebar-brand"
import { DashboardHeader } from "@/components/layout/dashboard-header"
import { SidebarFooter } from "@/components/layout/sidebar-footer"
import { SidebarNav } from "@/components/layout/sidebar-nav"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-[100dvh] bg-background">
      <aside className="flex w-[220px] shrink-0 flex-col border-r border-border bg-sidebar">
        <SidebarBrand />
        <SidebarNav />
        <SidebarFooter />
      </aside>
      <main className="flex flex-1 flex-col overflow-auto">
        <DashboardHeader />
        {children}
      </main>
    </div>
  )
}
