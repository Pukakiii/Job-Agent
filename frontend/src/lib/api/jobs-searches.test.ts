import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { listJobs } from "./jobs"
import { getSearch, listSearches, triggerSearch } from "./searches"

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  })
}

describe("jobs API", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("listJobs returns a JobRead array", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse([
        {
          id: "job-1",
          title: "Engineer",
          company: "Acme",
          location: "Remote",
          url: "https://example.com",
        },
      ]),
    )

    const result = await listJobs({ limit: 10, offset: 0 })

    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.data).toHaveLength(1)
      expect(result.data[0].title).toBe("Engineer")
    }
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/jobs?limit=10&offset=0",
      expect.any(Object),
    )
  })
})

describe("searches API", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("listSearches returns search summaries", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse([
        {
          id: "search-1",
          prompt: "React roles",
          created_at: "2026-06-01T00:00:00Z",
        },
      ]),
    )

    const result = await listSearches()

    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.data[0].prompt).toBe("React roles")
    }
  })

  it("getSearch returns embedded results", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({
        id: "search-1",
        prompt: "React roles",
        created_at: "2026-06-01T00:00:00Z",
        results: [
          {
            job: {
              id: "job-1",
              title: "Engineer",
              company: "Acme",
              location: "Remote",
              url: "https://example.com",
            },
            rank: 1,
            score: 0.9,
            explanation: "Strong match",
          },
        ],
      }),
    )

    const result = await getSearch("search-1")

    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.data.results).toHaveLength(1)
      expect(result.data.results[0].score).toBe(0.9)
    }
  })

  it("triggerSearch distinguishes 201 search from 202 ingest", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        {
          status: "ingesting",
          job_id: "ingest-1",
          message: "No jobs yet",
        },
        { status: 202 },
      ),
    )

    const ingestResult = await triggerSearch({
      cv_id: "cv-1",
      prompt: "Python jobs",
    })

    expect(ingestResult.ok).toBe(true)
    if (ingestResult.ok) {
      expect(ingestResult.data.kind).toBe("ingesting")
    }

    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        {
          id: "search-2",
          prompt: "Python jobs",
          created_at: "2026-06-02T00:00:00Z",
          results: [],
        },
        { status: 201 },
      ),
    )

    const searchResult = await triggerSearch({
      cv_id: "cv-1",
      prompt: "Python jobs",
    })

    expect(searchResult.ok).toBe(true)
    if (searchResult.ok) {
      expect(searchResult.data.kind).toBe("search")
    }
  })
})
