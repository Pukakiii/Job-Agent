"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useTheme } from "@teispace/next-themes"

import { BrandLogo } from "@/components/brand/brand-logo"
import { ClientMounted } from "@/components/home/client-mounted"
import { FadeIn } from "@/components/home/fade-in"
import { Particles } from "@/components/ui/particles"
import { ShimmerButton } from "@/components/ui/shimmer-button"
import { TypingAnimation } from "@/components/ui/typing-animation"
import { useIsClient } from "@/hooks/use-is-client"

const FEATURES = [
  "Semantic job matching",
  "AI-scored opportunities",
  "Auto-generated cover letters",
] as const

export function HomeHero() {
  const router = useRouter()
  const { resolvedTheme } = useTheme()
  const mounted = useIsClient()

  return (
    <main className="relative flex min-h-screen min-h-[100dvh] flex-col items-center justify-center overflow-hidden bg-background px-6 py-8 text-center">
      {mounted ? (
        <Particles
          key={resolvedTheme ?? "system"}
          className="absolute inset-0 h-full w-full"
          quantity={60}
          staticity={80}
          ease={80}
          size={0.8}
          vx={0.02}
          vy={0.01}
        />
      ) : null}

      <div className="relative z-10 flex w-full max-w-2xl flex-col items-center">
        <FadeIn>
          <BrandLogo className="mb-10" />
        </FadeIn>

        <FadeIn delay={0.05}>
          <p className="mb-6 text-xs font-medium uppercase tracking-widest text-primary">
            AI-powered job search
          </p>
        </FadeIn>

        <h1 className="max-w-xl text-5xl leading-tight font-semibold tracking-tight text-foreground">
          <ClientMounted fallback={<span>Find the right job,</span>}>
            <TypingAnimation
              as="span"
              className="inline font-medium"
              duration={40}
              showCursor={false}
            >
              Find the right job,
            </TypingAnimation>
          </ClientMounted>{" "}
          <span className="text-primary font-logo font-bold">FASTER.</span>
        </h1>

        <FadeIn delay={0.15} className="mt-6 max-w-md">
          <p className="text-base leading-relaxed text-muted-foreground">
            Job Agent collects, scores, and matches opportunities to your CV —
            automatically. No more manual searching.
          </p>
        </FadeIn>

        <FadeIn delay={0.25} className="mt-10">
          <div className="flex flex-wrap justify-center gap-3">
            <ClientMounted
              fallback={
                <Link
                  href="/login"
                  className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground"
                >
                  Get started
                </Link>
              }
            >
              <ShimmerButton
                type="button"
                borderRadius="6px"
                background="var(--primary)"
                shimmerColor="var(--primary-foreground)"
                shimmerDuration="4s"
                className="h-10 rounded-md px-6 text-sm font-medium text-primary-foreground shadow-none"
                onClick={() => router.push("/login")}
              >
                Get started
              </ShimmerButton>
            </ClientMounted>
            <Link
              href="/login"
              className="inline-flex h-10 items-center justify-center rounded-md border border-border px-6 text-sm font-medium text-muted-foreground transition-colors hover:border-[var(--color-border-em)] hover:text-foreground"
            >
              Sign in
            </Link>
          </div>
        </FadeIn>

        <FadeIn delay={0.35} className="mt-16">
          <div className="flex flex-wrap justify-center gap-8">
            {FEATURES.map((feature) => (
              <div
                key={feature}
                className="flex items-center gap-2 text-sm text-muted-foreground"
              >
                <div className="size-1.5 rounded-full bg-primary" />
                {feature}
              </div>
            ))}
          </div>
        </FadeIn>

        <FadeIn delay={0.45} className="mt-12">
          <p className="text-xs text-[var(--color-text-faint)]">
            No credit card required · Free to use during beta
          </p>
        </FadeIn>
      </div>
    </main>
  )
}
