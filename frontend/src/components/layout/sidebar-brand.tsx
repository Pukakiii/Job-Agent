import Image from "next/image"
import Link from "next/link"

import { cn } from "@/lib/utils"

type SidebarBrandProps = {
  className?: string
}

export function SidebarBrand({ className }: SidebarBrandProps) {
  return (
    <Link
      href="/dashboard"
      className={cn(
        "flex h-14 shrink-0 items-center gap-2.5 border-b border-border px-4",
        className,
      )}
    >
      <Image
        src="/job-agent-logo.svg"
        alt=""
        width={28}
        height={28}
        className="size-7 shrink-0"
      />
      <span className="font-logo text-lg font-bold tracking-tight text-foreground">
        Job Agent
      </span>
    </Link>
  )
}
