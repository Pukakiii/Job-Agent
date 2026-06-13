import { cn } from "@/lib/utils"
import Image from "next/image"
import { Backlight } from "@/components/ui/backlight"

type BrandLogoProps = {
  className?: string
}

export function BrandLogo({ className }: BrandLogoProps) {
  return (
    <div className={cn("flex items-center gap-2.5" , className)}>
      <Backlight>
        <Image src="/job-agent-logo.svg" alt="Job Agent" width={32} height={32} className="size-20 hover:brightness-110 hover:scale-105 transition-colors duration-500 cursor-pointer" />   
      </Backlight>
      <span className="text-3xl font-logo font-bold tracking-tight text-foreground self-end">
        Job Agent
      </span>
    </div>
  )
}
