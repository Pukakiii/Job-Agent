"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { FolderKanban } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import { ErrorBanner } from "@/components/ui/error-banner"
import { LoadingSkeleton } from "@/components/ui/loading-skeleton"
import {
  listApplications,
  updateApplicationStatus,
  type Application,
  type ApplicationStatus,
} from "@/lib/api/applications"
import { cn } from "@/lib/utils"
import { toast } from "@/lib/toast"

const KANBAN_COLUMNS: {
  status: ApplicationStatus
  label: string
  badgeClassName: string
}[] = [
  {
    status: "saved",
    label: "Saved",
    badgeClassName:
      "border-border bg-transparent text-muted-foreground",
  },
  {
    status: "applied",
    label: "Applied",
    badgeClassName:
      "border-[var(--color-accent-border)] bg-[var(--color-accent-subtle)] text-[var(--color-accent-hover)]",
  },
  {
    status: "interview",
    label: "Interview",
    badgeClassName:
      "border-[color-mix(in_oklch,var(--color-success)_40%,transparent)] bg-[color-mix(in_oklch,var(--color-success)_12%,transparent)] text-[var(--color-success)]",
  },
  {
    status: "offer",
    label: "Offer",
    badgeClassName:
      "border-[color-mix(in_oklch,var(--color-info)_40%,transparent)] bg-[color-mix(in_oklch,var(--color-info)_12%,transparent)] text-[var(--color-info)]",
  },
  {
    status: "rejected",
    label: "Rejected",
    badgeClassName:
      "border-[color-mix(in_oklch,var(--color-error)_40%,transparent)] bg-[color-mix(in_oklch,var(--color-error)_12%,transparent)] text-[var(--color-error)]",
  },
]

const NEXT_STATUS: Partial<Record<ApplicationStatus, ApplicationStatus>> = {
  saved: "applied",
  applied: "interview",
  interview: "offer",
}

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function load() {
      const result = await listApplications({ limit: 100 })
      if (!active) return

      if (!result.ok) {
        setError(result.error.message)
      } else {
        setApplications(result.data)
      }
      setLoading(false)
    }

    void load()

    return () => {
      active = false
    }
  }, [])

  function countByStatus(status: ApplicationStatus): number {
    return applications.filter((app) => app.status === status).length
  }

  async function advanceStatus(app: Application) {
    const nextStatus = NEXT_STATUS[app.status]
    if (!nextStatus) return

    const result = await updateApplicationStatus(app.id, { status: nextStatus })
    if (!result.ok) {
      setError(result.error.message)
      return
    }

    setApplications((current) =>
      current.map((item) => (item.id === app.id ? result.data : item)),
    )
    toast.success(`Moved to ${nextStatus}`)
  }

  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-4 py-5 sm:px-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            Applications
          </h1>
          <p className="text-sm text-muted-foreground">
            Track every role from saved to final outcome.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          nativeButton={false}
          render={<Link href="/dashboard/jobs" />}
        >
          Browse jobs
        </Button>
      </header>

      {error ? (
        <ErrorBanner message={error} onDismiss={() => setError(null)} />
      ) : null}

      {loading ? (
        <LoadingSkeleton rows={6} />
      ) : (
        <div className="grid min-h-[480px] grid-cols-1 gap-4 lg:grid-cols-5">
          {KANBAN_COLUMNS.map((column) => {
            const columnApps = applications.filter(
              (app) => app.status === column.status,
            )

            return (
              <Card key={column.status} className="flex flex-col border-border">
                <CardHeader className="gap-2 border-b border-border pb-3">
                  <div className="flex items-center justify-between gap-2">
                    <Badge className={cn(column.badgeClassName)}>
                      {column.label}
                    </Badge>
                    <span className="font-mono text-xs text-muted-foreground tabular-nums">
                      {countByStatus(column.status)}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-1 flex-col gap-2 px-3 py-3">
                  {columnApps.length === 0 ? (
                    <div className="flex flex-1 flex-col items-center justify-center rounded-md border border-dashed border-border px-2 py-8 text-center">
                      <p className="text-xs text-muted-foreground">
                        No {column.label.toLowerCase()} applications
                      </p>
                    </div>
                  ) : (
                    columnApps.map((app) => (
                      <div
                        key={app.id}
                        className="rounded-md border border-border bg-card px-3 py-2 text-sm"
                      >
                        <p className="font-medium">
                          {app.job?.title ?? `Job ${app.job_id.slice(0, 8)}`}
                        </p>
                        {app.job?.company ? (
                          <p className="text-xs text-muted-foreground">
                            {app.job.company}
                          </p>
                        ) : null}
                        {app.notes ? (
                          <p className="mt-1 text-xs text-muted-foreground">
                            {app.notes}
                          </p>
                        ) : null}
                        {NEXT_STATUS[app.status] ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="mt-2 h-7 px-2"
                            onClick={() => void advanceStatus(app)}
                          >
                            Move to {NEXT_STATUS[app.status]}
                          </Button>
                        ) : null}
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {!loading && applications.length === 0 ? (
        <Card className="border-border">
          <CardContent>
            <EmptyState
              icon={FolderKanban}
              title="Your pipeline is empty"
              description="Save jobs from your matches or add applications manually to track progress across every stage."
              action={
                <Button
                  size="sm"
                  nativeButton={false}
                  render={<Link href="/dashboard/jobs" />}
                >
                  Browse jobs
                </Button>
              }
            />
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
