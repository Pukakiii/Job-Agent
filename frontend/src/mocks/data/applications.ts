import type { Application } from "@/lib/api/applications"
import { jobs } from "./jobs"

export const applications: Application[] = [
  {
    id: "app_001",
    job_id: "job_001",
    status: "applied",
    notes: "Applied through their website directly.",
    created_at: "2026-06-11T10:00:00Z",
    updated_at: "2026-06-11T10:00:00Z",
    job: jobs[0],
  },
  {
    id: "app_002",
    job_id: "job_002",
    status: "interview",
    notes: "HR call scheduled for Monday.",
    created_at: "2026-06-08T14:00:00Z",
    updated_at: "2026-06-10T09:00:00Z",
    job: jobs[1],
  },
  {
    id: "app_003",
    job_id: "job_003",
    status: "saved",
    notes: null,
    created_at: "2026-06-09T11:00:00Z",
    updated_at: "2026-06-09T11:00:00Z",
    job: jobs[2],
  },
  {
    id: "app_004",
    job_id: "job_004",
    status: "rejected",
    notes: "Got a rejection email after technical test.",
    created_at: "2026-06-05T10:00:00Z",
    updated_at: "2026-06-07T16:00:00Z",
    job: jobs[3],
  },
]
