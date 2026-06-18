import { http, HttpResponse } from "msw"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import type { ReactElement } from "react"
import { describe, expect, it, vi } from "vitest"

import AuthProvider, { useAuthContext } from "./AuthProvider"
import { userMe } from "@/mocks/data/users"
import { server } from "@/test/server"

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
  it("loads the current user on mount", async () => {
    renderAuth(<AuthProbe />)

    expect(screen.getByTestId("loading")).toHaveTextContent("loading")

    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("ready")
    })

    expect(screen.getByTestId("email")).toHaveTextContent(userMe.email)
  })

  it("populates user after successful login", async () => {
    server.use(
      http.get("/api/v1/users/me", () => {
        return HttpResponse.json(userMe)
      }),
    )

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
    server.use(
      http.get("/api/v1/users/me", () => {
        return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 })
      }),
      http.post("/api/v1/auth/jwt/login", () => {
        return HttpResponse.json(
          { detail: "Invalid credentials" },
          { status: 400 },
        )
      }),
    )

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
