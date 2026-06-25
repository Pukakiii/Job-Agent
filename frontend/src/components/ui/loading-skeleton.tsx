import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

type LoadingSkeletonProps = {
  className?: string
  rows?: number
}

export function LoadingSkeleton({
  className,
  rows = 3,
}: LoadingSkeletonProps) {
  return (
    <div className={cn("flex flex-col gap-3", className)} aria-busy="true">
      <Skeleton className="h-8 w-1/3" />
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton key={index} className="h-16 w-full" />
      ))}
    </div>
  )
}

export function LoadingSkeletonCards({
  className,
  count = 4,
}: {
  className?: string
  count?: number
}) {
  return (
    <div
      className={cn("grid gap-4 sm:grid-cols-2 lg:grid-cols-4", className)}
      aria-busy="true"
    >
      {Array.from({ length: count }).map((_, index) => (
        <Skeleton key={index} className="h-24 w-full" />
      ))}
    </div>
  )
}
