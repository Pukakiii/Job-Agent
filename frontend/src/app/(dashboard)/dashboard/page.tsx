"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight, Briefcase, FolderKanban, Upload } from "lucide-react"

import { ErrorBanner } from "@/components/ui/error-banner"
import { LoadingSkeletonCards } from "@/components/ui/loading-skeleton"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { listApplications } from "@/lib/api/applications"
import { listCVs } from "@/lib/api/cvs"
import { listJobs } from "@/lib/api/jobs"
import { listSearches } from "@/lib/api/searches"

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
  const [stats, setStats] = useState({
    jobs: 0,
    applications: 0,
    cvs: 0,
    searches: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadStats() {
      const [jobsRes, appsRes, cvsRes, searchesRes] = await Promise.all([
        listJobs({ limit: 100 }),
        listApplications({ limit: 100 }),
        listCVs({ limit: 100 }),
        listSearches({ limit: 100 }),
      ])

      if (!active) return

      if (!jobsRes.ok || !appsRes.ok || !cvsRes.ok || !searchesRes.ok) {
        const message =
          (!jobsRes.ok && jobsRes.error.message) ||
          (!appsRes.ok && appsRes.error.message) ||
          (!cvsRes.ok && cvsRes.error.message) ||
          (!searchesRes.ok && searchesRes.error.message) ||
          "Failed to load dashboard stats"
        setError(message)
        setLoading(false)
        return
      }

      const activeApplications = appsRes.data.filter(
        (app) => app.status !== "rejected",
      ).length

      setStats({
        jobs: jobsRes.data.length,
        applications: activeApplications,
        cvs: cvsRes.data.length,
        searches: searchesRes.data.length,
      })
      setLoading(false)
    }

    void loadStats()

    return () => {
      active = false
    }
  }, [])

  const overviewStats = [
    { label: "Matched jobs", value: String(stats.jobs) },
    { label: "Active applications", value: String(stats.applications) },
    { label: "CVs uploaded", value: String(stats.cvs) },
    { label: "Searches run", value: String(stats.searches) },
  ]

  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-4 py-5 sm:px-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Your job search command center. Start by uploading a CV or running a
          match.
        </p>
      </header>

      {error ? (
        <ErrorBanner message={error} onDismiss={() => setError(null)} />
      ) : null}

      {loading ? (
        <LoadingSkeletonCards />
      ) : (
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {overviewStats.map((stat) => (
            <Card
              key={stat.label}
              className="border-border bg-[var(--color-accent-subtle)]"
            >
              <CardContent className="px-4 py-4">
                <p className="font-mono text-[28px] font-semibold tabular-nums text-foreground">
                  {stat.value}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {stat.label}
                </p>
              </CardContent>
            </Card>
          ))}
        </section>
      )}

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
