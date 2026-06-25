/** localStorage override for dev; falls back to NEXT_PUBLIC_ENABLE_MSW. */
export const MSW_STORAGE_KEY = "jobagent_enable_msw"

export function getDefaultMswEnabled(): boolean {
  return process.env.NEXT_PUBLIC_ENABLE_MSW === "true"
}

export function isMswEnabled(): boolean {
  if (typeof window === "undefined") {
    return getDefaultMswEnabled()
  }

  const stored = localStorage.getItem(MSW_STORAGE_KEY)
  if (stored === "true") return true
  if (stored === "false") return false
  return getDefaultMswEnabled()
}

export function setMswEnabled(enabled: boolean): void {
  localStorage.setItem(MSW_STORAGE_KEY, enabled ? "true" : "false")
}

export function clearMswOverride(): void {
  localStorage.removeItem(MSW_STORAGE_KEY)
}

export function getMswSource(): "override-on" | "override-off" | "env" {
  if (typeof window === "undefined") return "env"

  const stored = localStorage.getItem(MSW_STORAGE_KEY)
  if (stored === "true") return "override-on"
  if (stored === "false") return "override-off"
  return "env"
}
