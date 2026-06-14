import type { Search, SearchResult } from "@/lib/api/searches"
import { jobs } from "./jobs"

export const searches: Search[] = [
  {
    id: "search_001",
    prompt: "React developer roles in Warsaw",
    created_at: "2026-06-10T12:00:00Z",
  },
  {
    id: "search_002",
    prompt: "Remote TypeScript positions",
    created_at: "2026-06-09T09:00:00Z",
  },
]

export const searchResults: Record<string, SearchResult[]> = {
  search_001: [
    {
      job: jobs[0],
      rank: 1,
      score: 0.95,
      explanation: "Strong match for React experience in Warsaw.",
    },
    {
      job: jobs[1],
      rank: 2,
      score: 0.87,
      explanation: "Good fit for frontend engineering skills.",
    },
    {
      job: jobs[2],
      rank: 3,
      score: 0.76,
      explanation: "Relevant React role in Kraków.",
    },
  ],
  search_002: [
    {
      job: jobs[3],
      rank: 1,
      score: 0.91,
      explanation: "Senior TypeScript role matching your profile.",
    },
    {
      job: jobs[4],
      rank: 2,
      score: 0.82,
      explanation: "Remote full stack opportunity.",
    },
  ],
}
