import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  createApplication,
  listApplications,
  updateApplicationStatus,
} from "./applications"
import { deleteCV, listCVs, uploadCV } from "./cvs"

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  })
}

describe("cvs API", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("listCVs returns CVRead array", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse([
        {
          id: "cv-1",
          original_filename: "resume.pdf",
          content_type: "application/pdf",
          created_at: "2026-06-01T00:00:00Z",
        },
      ]),
    )

    const result = await listCVs()

    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.data[0].original_filename).toBe("resume.pdf")
    }
  })

  it("uploadCV posts multipart form data to /cvs", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        {
          id: "cv-2",
          original_filename: "new.pdf",
          created_at: "2026-06-02T00:00:00Z",
        },
        { status: 201 },
      ),
    )

    const file = new File(["cv"], "new.pdf", { type: "application/pdf" })
    const result = await uploadCV(file)

    expect(result.ok).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/cvs",
      expect.objectContaining({ method: "POST" }),
    )
  })

  it("deleteCV issues DELETE request", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }))

    const result = await deleteCV("cv-1")

    expect(result.ok).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/cvs/cv-1",
      expect.objectContaining({ method: "DELETE" }),
    )
  })
})

describe("applications API", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("listApplications returns application array", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse([
        {
          id: "app-1",
          job_id: "job-1",
          cv_id: null,
          status: "saved",
          notes: null,
          applied_at: null,
          created_at: "2026-06-01T00:00:00Z",
          updated_at: "2026-06-01T00:00:00Z",
        },
      ]),
    )

    const result = await listApplications({ status: "saved" })

    expect(result.ok).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/applications?status=saved",
      expect.any(Object),
    )
  })

  it("createApplication posts job_id", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        {
          id: "app-2",
          job_id: "job-2",
          cv_id: null,
          status: "saved",
          notes: null,
          applied_at: null,
          created_at: "2026-06-02T00:00:00Z",
          updated_at: "2026-06-02T00:00:00Z",
        },
        { status: 201 },
      ),
    )

    const result = await createApplication({ job_id: "job-2" })

    expect(result.ok).toBe(true)
  })

  it("updateApplicationStatus uses PUT", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({
        id: "app-1",
        job_id: "job-1",
        cv_id: null,
        status: "applied",
        notes: null,
        applied_at: "2026-06-03T00:00:00Z",
        created_at: "2026-06-01T00:00:00Z",
        updated_at: "2026-06-03T00:00:00Z",
      }),
    )

    const result = await updateApplicationStatus("app-1", {
      status: "applied",
    })

    expect(result.ok).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/applications/app-1",
      expect.objectContaining({ method: "PUT" }),
    )
  })
})
