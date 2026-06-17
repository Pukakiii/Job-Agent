import type { Application, ApplicationStatus } from "@/lib/api/applications"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"

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

const applications: Application[] = []

function countByStatus(status: ApplicationStatus): number {
  return applications.filter((app) => app.status === status).length
}

export default function ApplicationsPage() {
  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-6 py-5">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            Applications
          </h1>
          <p className="text-sm text-muted-foreground">
            Track every role from saved to final outcome.
          </p>
        </div>
        <Button variant="outline" size="sm">
          Add application
        </Button>
      </header>

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
                      <p className="font-medium">Job {app.job_id.slice(0, 8)}</p>
                      {app.notes ? (
                        <p className="mt-1 text-xs text-muted-foreground">
                          {app.notes}
                        </p>
                      ) : null}
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {applications.length === 0 ? (
        <Card className="border-border">
          <CardContent className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <CardTitle className="text-sm font-medium">
              Your pipeline is empty
            </CardTitle>
            <CardDescription className="max-w-md">
              Save jobs from your matches or add applications manually to track
              progress across every stage.
            </CardDescription>
            <Button className="mt-2" size="sm">
              Browse jobs
            </Button>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
