import * as React from "react"

import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

type FormFieldProps = {
  label: string
  htmlFor: string
  error?: string
  showError?: boolean
  className?: string
  children: React.ReactNode
}

function FormField({
  label,
  htmlFor,
  error,
  showError = false,
  className,
  children,
}: FormFieldProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
      {showError && error ? (
        <p className="text-xs text-destructive">{error}</p>
      ) : null}
    </div>
  )
}

export { FormField }
