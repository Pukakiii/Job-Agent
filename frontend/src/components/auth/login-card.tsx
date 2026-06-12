"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

import { BrandLogo } from "@/components/auth/brand-logo"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { login } from "@/lib/api/auth"
import { cn } from "@/lib/utils"

type Field = "email" | "password"

type Touched = Record<Field, boolean>

function validateEmail(value: string): string | undefined {
  if (!value) return "Email is required"
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return "Enter a valid email"
}

function validatePassword(value: string): string | undefined {
  if (!value) return "Password is required"
  if (value.length < 8) return "Password must be at least 8 characters"
}

function showFieldError(
  field: Field,
  touched: Touched,
  submitAttempted: boolean,
  error?: string,
) {
  return submitAttempted && touched[field] && !!error
}

export function LoginCard() {
  const router = useRouter()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [touched, setTouched] = useState<Touched>({ email: false, password: false })
  const [submitAttempted, setSubmitAttempted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)

  const errors = {
    email: validateEmail(email),
    password: validatePassword(password),
  }

  function handleBlur(field: Field) {
    setTouched((prev) => ({ ...prev, [field]: true }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitAttempted(true)
    setTouched({ email: true, password: true })

    if (errors.email || errors.password) return

    setLoading(true)
    setApiError(null)

    const result = await login({ username: email, password })

    setLoading(false)

    if (result.ok) {
      router.push("/dashboard")
    } else {
      setApiError(result.error.message)
    }
  }

  const showEmailError = showFieldError(
    "email",
    touched,
    submitAttempted,
    errors.email,
  )
  const showPasswordError = showFieldError(
    "password",
    touched,
    submitAttempted,
    errors.password,
  )

  return (
    <div className="flex min-h-screen min-h-[100dvh] flex-col items-center justify-center bg-background px-4 py-12">
      <BrandLogo className="mb-8" />

      <div className="w-full max-w-[400px] rounded-lg border border-border bg-card p-8">
        <div className="mb-8">
          <h1 className="text-lg font-semibold text-foreground">Sign in</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Sign in to your account
          </p>
        </div>

        {apiError && (
          <div className="mb-6 flex items-start justify-between gap-3 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3">
            <p className="text-sm text-destructive">{apiError}</p>
            <button
              type="button"
              onClick={() => setApiError(null)}
              className="mt-0.5 text-lg leading-none text-destructive/70 hover:text-destructive"
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onBlur={() => handleBlur("email")}
              placeholder="you@example.com"
              aria-invalid={showEmailError}
              className={cn(
                "h-10 rounded-md border-border",
                showEmailError && "border-destructive",
              )}
            />
            {showEmailError && (
              <p className="text-xs text-destructive">{errors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => handleBlur("password")}
              placeholder="••••••••"
              aria-invalid={showPasswordError}
              className={cn(
                "h-10 rounded-md border-border",
                showPasswordError && "border-destructive",
              )}
            />
            {showPasswordError && (
              <p className="text-xs text-destructive">{errors.password}</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="h-10 w-full rounded-md hover:bg-[var(--color-accent-hover)]"
          >
            {loading ? "Signing in…" : "Sign in"}
          </Button>
        </form>

        <p className="mt-8 text-center text-sm text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            className="font-medium text-primary hover:underline"
          >
            Register
          </Link>
        </p>
      </div>
    </div>
  )
}
