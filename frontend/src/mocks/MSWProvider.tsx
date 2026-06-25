"use client"

import { useEffect } from "react"

export default function MSWProvider({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENABLE_MSW !== "true") return

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
