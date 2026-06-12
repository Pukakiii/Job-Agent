import { cn } from "@/lib/utils"
import Image from "next/image"
type BrandLogoProps = {
  className?: string
}

export function BrandLogo({ className }: BrandLogoProps) {
  return (
    <div className={cn("flex items-center gap-2.5" , className)}>
        <Image src="/job-agent.svg" alt="Job Agent" width={32} height={32} className="size-20" />   
      <span className="text-3xl font-semibold tracking-tight text-foreground self-end">
        Job Agent
      </span>
    </div>
  )
}
