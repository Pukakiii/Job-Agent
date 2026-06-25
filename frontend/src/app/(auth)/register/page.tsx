"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

import { BrandLogo } from "@/components/brand/brand-logo"
import { FormField } from "@/components/forms"
import { BlurFade } from "@/components/ui/magic/blur-fade"
import { Particles } from "@/components/ui/magic/particles"
import { ShimmerButton } from "@/components/ui/magic/shimmer-button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useIsClient } from "@/hooks/use-is-client"
import { register } from "@/lib/api/auth"
import {
  validateConfirmPassword,
  validateEmail,
  validatePassword,
} from "@/lib/validation/auth"
import { cn } from "@/lib/utils"

type Field = "email" | "password" | "confirmPassword"

type Touched = Record<Field, boolean>

function showFieldError(
  field: Field,
  touched: Touched,
  error?: string,
): boolean {
  return touched[field] && !!error
}

export default function RegisterPage() {
  const router = useRouter()
  const mounted = useIsClient()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [touched, setTouched] = useState<Touched>({
    email: false,
    password: false,
    confirmPassword: false,
  })
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)

  const errors = {
    email: validateEmail(email),
    password: validatePassword(password),
    confirmPassword: validateConfirmPassword(password, confirmPassword),
  }

  function handleBlur(field: Field) {
    setTouched((prev) => ({ ...prev, [field]: true }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setTouched({ email: true, password: true, confirmPassword: true })

    if (errors.email || errors.password || errors.confirmPassword) return

    setLoading(true)
    setApiError(null)

    const result = await register({ email, password })

    setLoading(false)

    if (result.ok) {
      router.push("/login?registered=true")
    } else {
      setApiError(result.error.message)
    }
  }

  const showEmailError = showFieldError("email", touched, errors.email)
  const showPasswordError = showFieldError("password", touched, errors.password)
  const showConfirmPasswordError = showFieldError(
    "confirmPassword",
    touched,
    errors.confirmPassword,
  )

  const logo = <BrandLogo className="mb-8" />

  const card = (
    <Card variant="glass" className="w-full max-w-[380px] gap-0 p-8">
      <CardHeader className="gap-1 p-0 pb-7">
        <CardTitle className="text-lg font-semibold text-foreground">
          Create account
        </CardTitle>
        <CardDescription>Start finding better jobs today</CardDescription>
      </CardHeader>

      <CardContent className="p-0">
        {apiError && (
          <div className="mb-5 flex items-start justify-between gap-3 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3">
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

        <form onSubmit={handleSubmit} noValidate className="space-y-5">
          <FormField
            label="Email"
            htmlFor="email"
            error={errors.email}
            showError={showEmailError}
          >
            <Input
              id="email"
              type="email"
              variant="glass"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onBlur={() => handleBlur("email")}
              placeholder="you@example.com"
              aria-invalid={showEmailError}
              className={cn(
                "py-2.5",
                showEmailError && "border-destructive",
              )}
            />
          </FormField>

          <FormField
            label="Password"
            htmlFor="password"
            error={errors.password}
            showError={showPasswordError}
          >
            <Input
              id="password"
              type="password"
              variant="glass"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => handleBlur("password")}
              placeholder="••••••••"
              aria-invalid={showPasswordError}
              className={cn(
                "py-2.5",
                showPasswordError && "border-destructive",
              )}
            />
          </FormField>

          <FormField
            label="Confirm password"
            htmlFor="confirmPassword"
            error={errors.confirmPassword}
            showError={showConfirmPasswordError}
          >
            <Input
              id="confirmPassword"
              type="password"
              variant="glass"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              onBlur={() => handleBlur("confirmPassword")}
              placeholder="••••••••"
              aria-invalid={showConfirmPasswordError}
              className={cn(
                "py-2.5",
                showConfirmPasswordError && "border-destructive",
              )}
            />
          </FormField>

          <ShimmerButton
            type="submit"
            disabled={loading}
            borderRadius="6px"
            background="var(--primary)"
            shimmerColor="var(--color-accent-hover)"
            shimmerDuration="4s"
            className="w-full rounded-md py-2.5 text-sm font-medium text-primary-foreground shadow-none"
          >
            {loading ? "Creating account…" : "Create account"}
          </ShimmerButton>
        </form>

        <p className="mt-5 text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-primary hover:underline"
          >
            Sign in
          </Link>
        </p>
      </CardContent>
    </Card>
  )

  return (
    <div className="relative flex min-h-[100dvh] w-full items-center justify-center overflow-hidden bg-background">
      {mounted && (
        <Particles
          className="absolute inset-0 z-0 h-full w-full"
          quantity={60}
          staticity={80}
          ease={80}
          size={0.8}
          color="var(--primary)"
          vx={0.02}
          vy={0.01}
        />
      )}

      <div className="relative z-10 flex w-full flex-col items-center justify-center px-4">
        <BlurFade delay={0} inView={false} suppressHydrationWarning>
          {logo}
        </BlurFade>
        <BlurFade
          delay={0.1}
          inView={false}
          suppressHydrationWarning
          className="w-full max-w-[380px]"
        >
          {card}
        </BlurFade>
      </div>
    </div>
  )
}
