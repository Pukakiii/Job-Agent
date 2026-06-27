import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import type { ReactElement } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import AuthProvider, { useAuthContext } from "./AuthProvider"
import type { User } from "@/lib/api/auth"

const userMe: User = {
  id: "usr_001",
  email: "test@example.com",
  is_active: true,
  is_verified: true,
  is_superuser: false,
}

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  })
}

function renderAuth(ui: ReactElement) {
  return render(<AuthProvider>{ui}</AuthProvider>)
}

function AuthProbe() {
  const { user, loading, login, logout } = useAuthContext()

  return (
    <div>
      <span data-testid="loading">{loading ? "loading" : "ready"}</span>
      <span data-testid="email">{user?.email ?? "none"}</span>
      <button
        type="button"
        onClick={() => {
          void login({ username: "test@example.com", password: "password123" })
        }}
      >
        Login
      </button>
      <button
        type="button"
        onClick={() => {
          void logout()
        }}
      >
        Logout
      </button>
    </div>
  )
}

describe("AuthProvider", () => {
  const fetchMock = vi.fn<typeof fetch>()

  // Route each request by path + method so one mock can serve the mount load,
  // login, and logout calls a single test makes.
  function route(handler: (path: string, method: string) => Response) {
    fetchMock.mockImplementation(
      (input: RequestInfo | URL, init?: RequestInit) => {
        const path = typeof input === "string" ? input : input.toString()
        const method = (init?.method ?? "GET").toUpperCase()
        return Promise.resolve(handler(path, method))
      },
    )
  }

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
  })

  afterEach(() => {
    fetchMock.mockReset()
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("loads the current user on mount", async () => {
    route((path) =>
      path.endsWith("/users/me")
        ? jsonResponse(userMe)
        : jsonResponse({}, { status: 404 }),
    )

    renderAuth(<AuthProbe />)

    expect(screen.getByTestId("loading")).toHaveTextContent("loading")

    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("ready")
    })

    expect(screen.getByTestId("email")).toHaveTextContent(userMe.email)
  })

  it("populates user after successful login", async () => {
    route((path) => {
      if (path.endsWith("/users/me")) return jsonResponse(userMe)
      if (path.endsWith("/auth/jwt/login")) return jsonResponse(userMe)
      return jsonResponse({}, { status: 404 })
    })

    const user = userEvent.setup()
    renderAuth(<AuthProbe />)

    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("ready")
    })

    await user.click(screen.getByRole("button", { name: "Login" }))

    await waitFor(() => {
      expect(screen.getByTestId("email")).toHaveTextContent(userMe.email)
    })
  })

  it("keeps user null after failed login", async () => {
    route((path) => {
      if (path.endsWith("/users/me")) {
        return jsonResponse({ detail: "Unauthorized" }, { status: 401 })
      }
      if (path.endsWith("/auth/jwt/login")) {
        return jsonResponse({ detail: "Invalid credentials" }, { status: 400 })
      }
      return jsonResponse({}, { status: 404 })
    })

    const user = userEvent.setup()
    renderAuth(<AuthProbe />)

    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("ready")
    })

    expect(screen.getByTestId("email")).toHaveTextContent("none")

    await user.click(screen.getByRole("button", { name: "Login" }))

    await waitFor(() => {
      expect(screen.getByTestId("email")).toHaveTextContent("none")
    })
  })

  it("clears user on logout", async () => {
    route((path) => {
      if (path.endsWith("/users/me")) return jsonResponse(userMe)
      if (path.endsWith("/auth/jwt/logout")) {
        return new Response(null, { status: 204 })
      }
      return jsonResponse({}, { status: 404 })
    })

    const user = userEvent.setup()
    renderAuth(<AuthProbe />)

    await waitFor(() => {
      expect(screen.getByTestId("email")).toHaveTextContent(userMe.email)
    })

    await user.click(screen.getByRole("button", { name: "Logout" }))

    await waitFor(() => {
      expect(screen.getByTestId("email")).toHaveTextContent("none")
    })
  })

  it("throws when useAuthContext is used outside the provider", () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {})

    expect(() => render(<AuthProbe />)).toThrow(
      "useAuthContext must be used within AuthProvider",
    )

    consoleError.mockRestore()
  })
})
