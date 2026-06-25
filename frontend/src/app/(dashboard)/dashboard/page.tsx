import Link from "next/link"
import { ArrowRight, Briefcase, FolderKanban, Upload } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const OVERVIEW_STATS = [
  { label: "Matched jobs", value: "0" },
  { label: "Active applications", value: "0" },
  { label: "CVs uploaded", value: "0" },
  { label: "Outreach drafts", value: "0" },
] as const

const QUICK_LINKS = [
  {
    href: "/dashboard/jobs",
    title: "Jobs",
    description: "Browse matched opportunities and saved listings.",
    icon: Briefcase,
  },
  {
    href: "/dashboard/cvs",
    title: "CVs",
    description: "Upload and manage your resume files.",
    icon: Upload,
  },
  {
    href: "/dashboard/applications",
    title: "Applications",
    description: "Track your pipeline from saved to offer.",
    icon: FolderKanban,
  },
] as const

export default function DashboardPage() {
  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-6 py-5">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Your job search command center. Start by uploading a CV or running a
          match.
        </p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {OVERVIEW_STATS.map((stat) => (
          <Card
            key={stat.label}
            className="border-border bg-[var(--color-accent-subtle)]"
          >
            <CardContent className="px-4 py-4">
              <p className="font-mono text-[28px] font-semibold tabular-nums text-foreground">
                {stat.value}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {QUICK_LINKS.map((link) => (
          <Card key={link.href} className="border-border">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <link.icon className="size-4 text-[var(--color-accent-hover)]" />
                <CardTitle className="text-sm">{link.title}</CardTitle>
              </div>
              <CardDescription>{link.description}</CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
              <Button
                variant="outline"
                size="sm"
                nativeButton={false}
                render={<Link href={link.href} />}
              >
                Open
                <ArrowRight />
              </Button>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  )
}
