"use client"

import { useEffect } from "react"

import { isMswEnabled } from "@/lib/msw-config"

export default function MSWProvider({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    if (!isMswEnabled()) return

    void import("./browser").then(({ worker }) =>
      worker.start({
        onUnhandledRequest: "bypass",
        serviceWorker: {
          url: "/mockServiceWorker.js",
        },
      }),
    )
  }, [])

  return <>{children}</>
}
