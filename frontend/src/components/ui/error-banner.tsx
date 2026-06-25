import { AlertCircle, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type ErrorBannerProps = {
  message: string
  onDismiss?: () => void
  className?: string
}

export function ErrorBanner({
  message,
  onDismiss,
  className,
}: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className={cn(
        "flex items-start justify-between gap-3 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3",
        className,
      )}
    >
      <div className="flex items-start gap-2">
        <AlertCircle className="mt-0.5 size-4 shrink-0 text-destructive" />
        <p className="text-sm text-destructive">{message}</p>
      </div>
      {onDismiss ? (
        <Button
          type="button"
          variant="ghost"
          size="icon-xs"
          onClick={onDismiss}
          aria-label="Dismiss error"
          className="text-destructive/70 hover:text-destructive"
        >
          <X className="size-4" />
        </Button>
      ) : null}
    </div>
  )
}
