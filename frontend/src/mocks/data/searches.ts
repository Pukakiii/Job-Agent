import type { Search, SearchResult } from "@/lib/api/searches"
import { jobs } from "./jobs"

export const searches: Search[] = [
  {
    id: "search_001",
    user_id: "usr_001",
    cv_id: "cv_001",
    status: "completed",
    created_at: "2026-06-10T12:00:00Z",
    completed_at: "2026-06-10T12:01:30Z",
    result_count: 3,
  },
  {
    id: "search_002",
    user_id: "usr_001",
    cv_id: "cv_001",
    status: "completed",
    created_at: "2026-06-09T09:00:00Z",
    completed_at: "2026-06-09T09:01:10Z",
    result_count: 2,
  },
]

export const searchResults: Record<string, SearchResult[]> = {
  search_001: [
    {
      id: "sr_001",
      search_id: "search_001",
      job_id: "job_001",
      similarity_score: 0.95,
      rank: 1,
      job: jobs[0],
    },
    {
      id: "sr_002",
      search_id: "search_001",
      job_id: "job_002",
      similarity_score: 0.87,
      rank: 2,
      job: jobs[1],
    },
    {
      id: "sr_003",
      search_id: "search_001",
      job_id: "job_003",
      similarity_score: 0.76,
      rank: 3,
      job: jobs[2],
    },
  ],
  search_002: [
    {
      id: "sr_004",
      search_id: "search_002",
      job_id: "job_004",
      similarity_score: 0.91,
      rank: 1,
      job: jobs[3],
    },
    {
      id: "sr_005",
      search_id: "search_002",
      job_id: "job_005",
      similarity_score: 0.82,
      rank: 2,
      job: jobs[4],
    },
  ],
}