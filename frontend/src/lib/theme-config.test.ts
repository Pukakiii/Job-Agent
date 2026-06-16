import { describe, expect, it } from "vitest"

import {
  THEME_STORAGE_KEY,
  buildThemeScriptOptions,
  themeConfig,
} from "./theme-config"

describe("buildThemeScriptOptions", () => {
  it("passes initialTheme through", () => {
    const options = buildThemeScriptOptions("dark")

    expect(options.initialTheme).toBe("dark")
  })

  it("uses shared storage key for cookie and storage", () => {
    const options = buildThemeScriptOptions(null)

    expect(options.storageKey).toBe(THEME_STORAGE_KEY)
    expect(options.cookieName).toBe(THEME_STORAGE_KEY)
    expect(themeConfig.storageKey).toBe(THEME_STORAGE_KEY)
  })

  it("emits transition lock CSS when transitions are disabled", () => {
    const options = buildThemeScriptOptions(null)

    expect(themeConfig.disableTransitionOnChange).toBe(true)
    expect(options.disableTransitionOnChange).toContain("transition:none")
  })
})
