"use client"

import { useSyncExternalStore } from "react"
import { motion } from "motion/react"

import { useIsClient } from "@/hooks/use-is-client"
import { cn } from "@/lib/utils"

type FadeInProps = {
  children: React.ReactNode
  className?: string
  delay?: number
}

function subscribeReducedMotion(onStoreChange: () => void) {
  const mq = window.matchMedia("(prefers-reduced-motion: reduce)")
  mq.addEventListener("change", onStoreChange)
  return () => mq.removeEventListener("change", onStoreChange)
}

function getReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches
}

export function FadeIn({ children, className, delay = 0 }: FadeInProps) {
  const mounted = useIsClient()
  const reduceMotion = useSyncExternalStore(
    subscribeReducedMotion,
    getReducedMotion,
    () => false,
  )

  if (!mounted || reduceMotion) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className={cn(className)}
      suppressHydrationWarning
    >
      {children}
    </motion.div>
  )
}
