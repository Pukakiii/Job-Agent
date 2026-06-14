import { Briefcase, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import type { Job } from "@/lib/api/jobs"

const JOB_STATS = [
  { label: "Total matches", value: "0" },
  { label: "Saved", value: "0" },
  { label: "High fit (80+)", value: "0" },
  { label: "New this week", value: "0" },
] as const

const jobs: Job[] = []

export default function JobsPage() {
  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-[1200px] flex-col gap-6 px-6 py-5">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Jobs</h1>
          <p className="text-sm text-muted-foreground">
            Semantic matches from your latest search.
          </p>
        </div>
        <Button>
          <Search />
          Run new search
        </Button>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {JOB_STATS.map((stat) => (
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

      <Card className="border-border">
        <CardHeader className="flex flex-row items-center justify-between gap-4 border-b border-border pb-4">
          <div>
            <CardTitle className="text-base">All jobs</CardTitle>
            <CardDescription>
              {jobs.length} listings from your most recent match.
            </CardDescription>
          </div>
          <div className="w-full max-w-xs">
            <Input type="search" placeholder="Filter by title or company…" />
          </div>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center gap-3 py-16 text-center">
          <Briefcase className="size-8 text-muted-foreground" />
          <div className="space-y-1">
            <p className="text-sm font-medium">No jobs yet</p>
            <p className="max-w-sm text-sm text-muted-foreground">
              Upload a CV and run a semantic search to see matched opportunities
              here.
            </p>
          </div>
          <Button variant="outline" size="sm">
            Upload CV
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
