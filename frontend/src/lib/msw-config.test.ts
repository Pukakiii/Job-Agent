import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  MSW_STORAGE_KEY,
  clearMswOverride,
  getDefaultMswEnabled,
  getMswSource,
  isMswEnabled,
  setMswEnabled,
} from "./msw-config"

describe("msw-config", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.unstubAllEnvs()
  })

  afterEach(() => {
    localStorage.clear()
    vi.unstubAllEnvs()
  })

  it("defaults from env when no override", () => {
    vi.stubEnv("NEXT_PUBLIC_ENABLE_MSW", "false")
    expect(getDefaultMswEnabled()).toBe(false)
    expect(isMswEnabled()).toBe(false)
    expect(getMswSource()).toBe("env")
  })

  it("respects env default true", () => {
    vi.stubEnv("NEXT_PUBLIC_ENABLE_MSW", "true")
    expect(isMswEnabled()).toBe(true)
  })

  it("localStorage override takes precedence over env", () => {
    vi.stubEnv("NEXT_PUBLIC_ENABLE_MSW", "false")
    setMswEnabled(true)
    expect(isMswEnabled()).toBe(true)
    expect(getMswSource()).toBe("override-on")

    setMswEnabled(false)
    expect(isMswEnabled()).toBe(false)
    expect(getMswSource()).toBe("override-off")
  })

  it("clearMswOverride restores env default", () => {
    vi.stubEnv("NEXT_PUBLIC_ENABLE_MSW", "true")
    setMswEnabled(false)
    expect(isMswEnabled()).toBe(false)
    clearMswOverride()
    expect(isMswEnabled()).toBe(true)
    expect(localStorage.getItem(MSW_STORAGE_KEY)).toBeNull()
  })
})
