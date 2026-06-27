import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, vi } from "vitest"

// Default to same-origin requests in tests; individual suites override as needed.
vi.stubEnv("NEXT_PUBLIC_API_URL", "")

afterEach(() => {
  cleanup()
})
