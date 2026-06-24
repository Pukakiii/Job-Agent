import { NextRequest } from "next/server"
import { describe, expect, it } from "vitest"

import { middleware } from "./middleware"

function createRequest(
  pathname: string,
  cookies: Record<string, string> = {},
): NextRequest {
  const url = new URL(pathname, "http://localhost:3000")
  const request = new NextRequest(url)

  for (const [name, value] of Object.entries(cookies)) {
    request.cookies.set(name, value)
  }

  return request
}

describe("middleware", () => {
  it("redirects unauthenticated users away from dashboard", () => {
    const response = middleware(createRequest("/dashboard"))

    expect(response.status).toBe(307)
    const location = response.headers.get("location")
    expect(location).toContain("/login")
    expect(location).toContain("from=%2Fdashboard")
  })

  it("allows dashboard access when auth cookie is present", () => {
    const response = middleware(
      createRequest("/dashboard", { jobagent_auth: "token" }),
    )

    expect(response.status).toBe(200)
    expect(response.headers.get("location")).toBeNull()
  })

  it("does not redirect public routes", () => {
    const response = middleware(createRequest("/login"))

    expect(response.status).toBe(200)
    expect(response.headers.get("location")).toBeNull()
  })

  it("sets Accept-CH header on all responses", () => {
    const response = middleware(createRequest("/"))

    expect(response.headers.get("Accept-CH")).toBeTruthy()
  })
})
