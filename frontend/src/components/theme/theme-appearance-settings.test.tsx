import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ThemeAppearanceSettings } from "./theme-appearance-settings"

const setTheme = vi.fn()

vi.mock("@teispace/next-themes", () => ({
  useTheme: () => ({
    theme: "dark",
    setTheme,
  }),
}))

describe("ThemeAppearanceSettings", () => {
  beforeEach(() => {
    setTheme.mockClear()
  })

  afterEach(() => {
    cleanup()
  })

  it("renders light, dark, and system options", () => {
    render(<ThemeAppearanceSettings />)

    expect(screen.getByRole("button", { name: "Light" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Dark" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "System" })).toBeInTheDocument()
  })

  it("calls setTheme when an option is clicked", async () => {
    const user = userEvent.setup()

    render(<ThemeAppearanceSettings />)

    await user.click(screen.getByRole("button", { name: "Light" }))

    expect(setTheme).toHaveBeenCalledWith("light")
  })

  it("highlights the active theme when mounted", async () => {
    render(<ThemeAppearanceSettings />)

    const darkButton = screen.getByRole("button", { name: "Dark" })

    await waitFor(() => {
      expect(darkButton.className).toContain("border-primary")
    })
  })
})
