"use client"

import type { ReactNode } from "react"

import { useIsClient } from "@/hooks/use-is-client"

type ClientMountedProps = {
  children: ReactNode
  fallback?: ReactNode
}

export function ClientMounted({ children, fallback = null }: ClientMountedProps) {
  const mounted = useIsClient()

  if (!mounted) return fallback

  return <>{children}</>
}
