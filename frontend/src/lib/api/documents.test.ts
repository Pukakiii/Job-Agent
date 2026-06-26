import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { generateDocument, listDocuments } from "./documents"

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  })
}

describe("documents API", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("listDocuments returns generated documents", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse([
        {
          id: "doc-1",
          job_id: "job-1",
          cv_id: "cv-1",
          doc_type: "resume",
          content: "# Resume",
          created_at: "2026-06-01T00:00:00Z",
        },
      ]),
    )

    const result = await listDocuments({ doc_type: "resume" })

    expect(result.ok).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/documents?doc_type=resume",
      expect.any(Object),
    )
  })

  it("generateDocument posts to /documents/generate", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        {
          id: "doc-2",
          job_id: "job-1",
          cv_id: null,
          doc_type: "cover_letter",
          content: "Dear hiring manager",
          created_at: "2026-06-02T00:00:00Z",
        },
        { status: 201 },
      ),
    )

    const result = await generateDocument({
      job_id: "job-1",
      doc_type: "cover_letter",
    })

    expect(result.ok).toBe(true)
  })
})
