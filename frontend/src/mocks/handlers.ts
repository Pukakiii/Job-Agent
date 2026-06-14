import { http, HttpResponse } from "msw"
import { userMe } from "./data/users"
import { jobs } from "./data/jobs"
import { searches, searchResults } from "./data/searches"
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
        "Set-Cookie": "fastapiusersauth=mock-jwt-token; Path=/; HttpOnly",
      },
    })
  }),

  http.post("/api/v1/auth/register", async ({ request }) => {
    const body = await request.json() as { email: string; password: string }
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
    const page = Number(url.searchParams.get("page") ?? 1)
    const size = Number(url.searchParams.get("size") ?? 20)
    const offset = (page - 1) * size
    return HttpResponse.json({
      items: jobs.slice(offset, offset + size),
      total: jobs.length,
      page,
      size,
    })
  }),

  http.get("/api/v1/jobs/:id", ({ params }) => {
    const job = jobs.find((j) => j.id === params.id)
    if (!job) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(job)
  }),

  http.get("/api/v1/jobs/:id/score", ({ params }) => {
    return HttpResponse.json({
      job_id: params.id,
      score: 0.88,
      explanation: "Strong match based on your React and TypeScript skills.",
      is_scam: false,
      scam_reason: null,
    })
  }),

  // ── Searches ─────────────────────────────────────────────────────
  http.get("/api/v1/searches", () => {
    return HttpResponse.json(searches)
  }),

  http.get("/api/v1/searches/:id", ({ params }) => {
    const search = searches.find((s) => s.id === params.id)
    if (!search) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(search)
  }),

  http.get("/api/v1/searches/:id/results", ({ params }) => {
    const results = searchResults[params.id as string] ?? []
    return HttpResponse.json(results)
  }),

  http.post("/api/v1/searches", async ({ request }) => {
    const body = await request.json() as { cv_id: string; prompt?: string }
    return HttpResponse.json(
      {
        id: "search_new",
        prompt: body.prompt ?? "New search",
        created_at: new Date().toISOString(),
      },
      { status: 202 }
    )
  }),

  // ── CVs ──────────────────────────────────────────────────────────
  http.get("/api/v1/cvs", () => {
    return HttpResponse.json(cvs)
  }),

  http.post("/api/v1/cvs/upload", async () => {
    return HttpResponse.json({
      id: "cv_new",
      original_filename: "uploaded_cv.pdf",
      created_at: new Date().toISOString(),
    })
  }),

  http.patch("/api/v1/cvs/:id/active", ({ params }) => {
    const cv = cvs.find((c) => c.id === params.id)
    if (!cv) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(cv)
  }),

  http.delete("/api/v1/cvs/:id", () => {
    return new HttpResponse(null, { status: 204 })
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
    const body = await request.json() as { job_id: string; status?: string }
    const job = jobs.find((j) => j.id === body.job_id)
    return HttpResponse.json({
      id: "app_new",
      job_id: body.job_id,
      status: body.status ?? "saved",
      notes: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      job: job ?? undefined,
    })
  }),

  http.patch("/api/v1/applications/:id", async ({ params, request }) => {
    const body = await request.json() as { status: string }
    const app = applications.find((a) => a.id === params.id)
    if (!app) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json({
      ...app,
      status: body.status,
      updated_at: new Date().toISOString(),
    })
  }),

  http.delete("/api/v1/applications/:id", () => {
    return new HttpResponse(null, { status: 204 })
  }),
]