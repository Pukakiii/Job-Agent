import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { apiRequest, get } from "./client"

function jsonResponse(
  body: unknown,
  init: ResponseInit = {},
): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  })
}

describe("apiRequest", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    vi.unstubAllEnvs()
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("returns parsed JSON on success", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ id: "1", name: "Job" }))

    const result = await apiRequest<{ id: string; name: string }>("/jobs")

    expect(result).toEqual({ ok: true, data: { id: "1", name: "Job" } })
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/jobs",
      expect.objectContaining({
        credentials: "include",
        headers: expect.objectContaining({
          Accept: "application/json",
          "Content-Type": "application/json",
        }),
      }),
    )
  })

  it("returns ok for 204 responses", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }))

    const result = await apiRequest<void>("/auth/jwt/logout", {
      method: "POST",
    })

    expect(result).toEqual({ ok: true, data: undefined })
  })

  it("maps FastAPI string detail to error message", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ detail: "Invalid credentials" }, { status: 400 }),
    )

    const result = await apiRequest("/auth/jwt/login", { method: "POST" })

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.status).toBe(400)
      expect(result.error.message).toBe("Invalid credentials")
    }
  })

  it("maps FastAPI validation array detail to error message", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        {
          detail: [
            { msg: "field required", type: "value_error.missing" },
            { msg: "invalid email", type: "value_error.email" },
          ],
        },
        { status: 422 },
      ),
    )

    const result = await get("/users/me")

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.message).toBe("field required; invalid email")
    }
  })

  it("returns network error when fetch throws", async () => {
    fetchMock.mockRejectedValueOnce(new Error("connection refused"))

    const result = await get("/users/me")

    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.status).toBe(0)
      expect(result.error.message).toBe("Network error")
    }
  })
})
