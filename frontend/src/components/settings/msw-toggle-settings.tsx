"use client"

import { useState } from "react"
import { RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  clearMswOverride,
  getDefaultMswEnabled,
  getMswSource,
  isMswEnabled,
  setMswEnabled,
} from "@/lib/msw-config"

function modeLabel(enabled: boolean): string {
  return enabled ? "Mock API (MSW)" : "Live backend"
}

export function MswToggleSettings() {
  const [enabled, setEnabled] = useState(() => isMswEnabled())
  const source = getMswSource()
  const envDefault = getDefaultMswEnabled()

  function applyAndReload(next: boolean) {
    setMswEnabled(next)
    window.location.reload()
  }

  function resetToEnvDefault() {
    clearMswOverride()
    window.location.reload()
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium">API mode</p>
          <p className="text-sm text-muted-foreground">
            Current: <span className="font-medium text-foreground">{modeLabel(enabled)}</span>
            {source !== "env" ? " (overridden in this browser)" : null}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            size="sm"
            variant={enabled ? "default" : "outline"}
            onClick={() => applyAndReload(true)}
          >
            Use mocks
          </Button>
          <Button
            type="button"
            size="sm"
            variant={!enabled ? "default" : "outline"}
            onClick={() => applyAndReload(false)}
          >
            Use live API
          </Button>
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Env default: {modeLabel(envDefault)} (
        <code className="rounded bg-muted px-1">NEXT_PUBLIC_ENABLE_MSW</code>
        ). Live mode proxies <code className="rounded bg-muted px-1">/api/v1</code>{" "}
        to the backend — start Docker Compose first. The page reloads after switching.
      </p>

      {source !== "env" ? (
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className="gap-2 px-0 text-muted-foreground hover:text-foreground"
          onClick={resetToEnvDefault}
        >
          <RefreshCw className="size-3.5" />
          Reset to env default ({modeLabel(envDefault)})
        </Button>
      ) : null}
    </div>
  )
}
