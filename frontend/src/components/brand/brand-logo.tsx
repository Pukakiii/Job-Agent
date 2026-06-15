import Image from "next/image"

import { Backlight } from "@/components/ui/backlight"
import { cn } from "@/lib/utils"

type BrandLogoProps = {
  className?: string
}

export function BrandLogo({ className }: BrandLogoProps) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <Backlight>
        <Image
          src="/job-agent-logo.svg"
          alt="Job Agent"
          width={32}
          height={32}
          loading="eager"
          priority
          className="size-20 cursor-pointer transition-all duration-500 hover:scale-105 hover:brightness-110"
        />
      </Backlight>
      <span className="self-end font-logo text-3xl font-bold tracking-tight text-foreground">
        Job Agent
      </span>
    </div>
  )
}
