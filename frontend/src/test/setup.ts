import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterAll, afterEach, beforeAll, vi } from "vitest"

import { server } from "./server"

vi.stubEnv("NEXT_PUBLIC_API_URL", "")

beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" })
})

afterEach(() => {
  server.resetHandlers()
  cleanup()
})

afterAll(() => {
  server.close()
  vi.unstubAllEnvs()
})
