import { ThemeProvider } from "@teispace/next-themes"
import { render, type RenderOptions } from "@testing-library/react"
import type { ReactElement, ReactNode } from "react"

import AuthProvider from "@/features/auth/AuthProvider"
import { themeConfig } from "@/lib/theme-config"

type ProviderOptions = {
  withAuth?: boolean
  withTheme?: boolean
}

function createWrapper(options: ProviderOptions = {}) {
  const { withAuth = true, withTheme = true } = options

  return function Wrapper({ children }: { children: ReactNode }) {
    let tree = children

    if (withAuth) {
      tree = <AuthProvider>{tree}</AuthProvider>
    }

    if (withTheme) {
      tree = (
        <ThemeProvider
          attribute={themeConfig.attribute}
          defaultTheme={themeConfig.defaultTheme}
          enableSystem={themeConfig.enableSystem}
          storageKey={themeConfig.storageKey}
          storage={themeConfig.storage}
          disableTransitionOnChange={themeConfig.disableTransitionOnChange}
        >
          {tree}
        </ThemeProvider>
      )
    }

    return tree
  }
}

export function renderWithProviders(
  ui: ReactElement,
  options?: RenderOptions & ProviderOptions,
) {
  const { withAuth, withTheme, ...renderOptions } = options ?? {}

  return render(ui, {
    wrapper: createWrapper({ withAuth, withTheme }),
    ...renderOptions,
  })
}
