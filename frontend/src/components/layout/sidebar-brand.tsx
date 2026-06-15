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
        "cursor-default flex h-14 shrink-0 items-center gap-2 border-b border-border px-4",
        className,
      )}
    >
       <div className={cn("flex items-center gap-0.5", className)}>
        <Image
          src="/job-agent-logo.svg"
          alt="Job Agent"
          width={32}
          height={32}
          loading="eager"
          priority
          className="size-10 cursor-pointer transition-all duration-500 hover:scale-105 hover:brightness-110"
        />
      <span className="cursor-pointer self-end font-logo text-xl font-bold tracking-tight text-foreground">
        Job Agent
      </span>
    </div>
    </Link>
  )
}
