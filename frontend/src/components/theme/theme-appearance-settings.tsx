"use client"

import { Monitor, Moon, Sun } from "lucide-react"
import { useTheme } from "@teispace/next-themes"

import { Button } from "@/components/ui/button"
import { useIsClient } from "@/hooks/use-is-client"
import { cn } from "@/lib/utils"

const THEME_OPTIONS = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
] as const

type ThemeValue = (typeof THEME_OPTIONS)[number]["value"]

export function ThemeAppearanceSettings() {
  const { theme, setTheme } = useTheme()
  const mounted = useIsClient()
  const activeTheme = (theme ?? "system") as ThemeValue

  return (
    <div className="flex flex-wrap gap-2">
      {THEME_OPTIONS.map((option) => {
        const Icon = option.icon
        const isActive = mounted && activeTheme === option.value

        return (
          <Button
            key={option.value}
            type="button"
            variant="outline"
            size="sm"
            disabled={!mounted}
            className={cn(
              "gap-2",
              isActive &&
                "border-primary bg-[var(--color-accent-subtle)] text-primary",
            )}
            onClick={() => {
              setTheme(option.value)
            }}
          >
            <Icon className="size-4" aria-hidden />
            {option.label}
          </Button>
        )
      })}
    </div>
  )
}
