import { describe, expect, it } from "vitest"

import { mergeJobsWithSearch } from "@/components/jobs/job-detail-drawer"
import type { Job } from "@/lib/api/jobs"
import type { SearchDetail } from "@/lib/api/searches"

describe("mergeJobsWithSearch", () => {
  const jobs: Job[] = [
    {
      id: "job-1",
      title: "Engineer",
      company: "Acme",
      location: "Berlin",
      url: "https://example.com/1",
    },
  ]

  it("attaches score and explanation from search results", () => {
    const search: SearchDetail = {
      id: "search-1",
      prompt: "python",
      created_at: "2026-06-01T00:00:00Z",
      results: [
        {
          job: jobs[0],
          rank: 1,
          score: 0.91,
          explanation: "Strong Python match",
        },
      ],
    }

    const merged = mergeJobsWithSearch(jobs, search)

    expect(merged[0].score).toBe(0.91)
    expect(merged[0].explanation).toBe("Strong Python match")
  })
})
