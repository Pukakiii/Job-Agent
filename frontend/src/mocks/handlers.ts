import { http, HttpResponse } from "msw"
import { userMe } from "./data/users"
import { jobs } from "./data/jobs"
import { searches, searchDetails } from "./data/searches"
import { cvs } from "./data/cvs"
import { applications } from "./data/applications"

export const handlers = [
  // ── Auth ─────────────────────────────────────────────────────────
  http.get("/api/v1/users/me", () => {
    return HttpResponse.json(userMe)
  }),

  http.post("/api/v1/auth/jwt/login", async () => {
    return HttpResponse.json(userMe, {
      headers: {
        "Set-Cookie": "jobagent_auth=mock-jwt-token; Path=/; HttpOnly",
      },
    })
  }),

  http.post("/api/v1/auth/register", async ({ request }) => {
    const body = (await request.json()) as { email: string; password: string }
    return HttpResponse.json({
      id: "usr_001",
      email: body.email,
      is_active: true,
      is_verified: false,
      is_superuser: false,
    })
  }),

  http.post("/api/v1/auth/jwt/logout", () => {
    return new HttpResponse(null, { status: 204 })
  }),

  // ── Jobs ─────────────────────────────────────────────────────────
  http.get("/api/v1/jobs", ({ request }) => {
    const url = new URL(request.url)
    const limit = Number(url.searchParams.get("limit") ?? 20)
    const offset = Number(url.searchParams.get("offset") ?? 0)
    return HttpResponse.json(jobs.slice(offset, offset + limit))
  }),

  http.get("/api/v1/jobs/:id", ({ params }) => {
    const job = jobs.find((j) => j.id === params.id)
    if (!job) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json({
      ...job,
      description: "Mock job description for local development.",
      source: "mock",
      posted_at: null,
      ingested_at: new Date().toISOString(),
    })
  }),

  // ── Searches ─────────────────────────────────────────────────────
  http.get("/api/v1/searches", () => {
    return HttpResponse.json(searches)
  }),

  http.get("/api/v1/searches/:id", ({ params }) => {
    const detail = searchDetails[params.id as string]
    if (!detail) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(detail)
  }),

  http.post("/api/v1/searches", async ({ request }) => {
    const body = (await request.json()) as {
      cv_id: string
      prompt?: string
    }
    const prompt = body.prompt ?? "New search"
    // Simulate corpus-empty ingest path (202) when prompt contains "ingest"
    if (prompt.toLowerCase().includes("ingest")) {
      return HttpResponse.json(
        {
          status: "ingesting",
          job_id: "mock-ingest-job",
          message: "No jobs yet — ingestion started. Try again shortly.",
        },
        { status: 202 },
      )
    }
    return HttpResponse.json(
      {
        id: "search_new",
        prompt,
        created_at: new Date().toISOString(),
        results: searchDetails.search_001?.results ?? [],
      },
      { status: 201 },
    )
  }),

  // ── CVs ──────────────────────────────────────────────────────────
  http.get("/api/v1/cvs", () => {
    return HttpResponse.json(cvs)
  }),

  http.post("/api/v1/cvs", async () => {
    return HttpResponse.json(
      {
        id: "cv_new",
        original_filename: "uploaded_cv.pdf",
        created_at: new Date().toISOString(),
      },
      { status: 201 },
    )
  }),

  http.delete("/api/v1/cvs/:id", () => {
    return new HttpResponse(null, { status: 204 })
  }),

  http.put("/api/v1/cvs/:id/active", ({ params }) => {
    const cv = cvs.find((item) => item.id === params.id)
    if (!cv) return new HttpResponse(null, { status: 404 })
    for (const item of cvs) {
      item.is_active = item.id === params.id
    }
    return HttpResponse.json({ ...cv, is_active: true })
  }),

  // ── Applications ─────────────────────────────────────────────────
  http.get("/api/v1/applications", ({ request }) => {
    const url = new URL(request.url)
    const status = url.searchParams.get("status")
    const filtered = status
      ? applications.filter((a) => a.status === status)
      : applications
    return HttpResponse.json(filtered)
  }),

  http.post("/api/v1/applications", async ({ request }) => {
    const body = (await request.json()) as {
      job_id: string
      status?: string
      notes?: string
    }
    const job = jobs.find((j) => j.id === body.job_id)
    return HttpResponse.json(
      {
        id: "app_new",
        job_id: body.job_id,
        cv_id: null,
        status: body.status ?? "saved",
        notes: body.notes ?? null,
        applied_at: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        job: job ?? undefined,
      },
      { status: 201 },
    )
  }),

  http.put("/api/v1/applications/:id", async ({ params, request }) => {
    const body = (await request.json()) as { status: string; notes?: string }
    const app = applications.find((a) => a.id === params.id)
    if (!app) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json({
      ...app,
      status: body.status,
      notes: body.notes ?? app.notes,
      updated_at: new Date().toISOString(),
    })
  }),

  http.delete("/api/v1/applications/:id", () => {
    return new HttpResponse(null, { status: 204 })
  }),
]
