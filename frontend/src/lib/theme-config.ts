export const THEME_STORAGE_KEY = "job-agent-theme"

export const themeConfig = {
  attribute: "class" as const,
  defaultTheme: "system",
  enableSystem: true,
  storageKey: THEME_STORAGE_KEY,
  storage: "hybrid" as const,
  disableTransitionOnChange: true,
}

export const themeServerOptions = {
  cookieName: THEME_STORAGE_KEY,
  themes: ["light", "dark", "system"],
}

const THEME_TRANSITION_LOCK =
  "*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}"

export function buildThemeScriptOptions(initialTheme: string | null) {
  return {
    attribute: themeConfig.attribute,
    defaultTheme: themeConfig.defaultTheme,
    enableSystem: themeConfig.enableSystem,
    storageKey: themeConfig.storageKey,
    storageMode: "hybrid" as const,
    cookieName: THEME_STORAGE_KEY,
    disableTransitionOnChange: themeConfig.disableTransitionOnChange
      ? THEME_TRANSITION_LOCK
      : null,
    initialTheme,
  }
}
