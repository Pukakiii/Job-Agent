'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { login } from '@/lib/api/auth';
import type { LoginRequest } from '@/lib/api/auth';
import type { ApiResult } from '@/lib/api/client';

// Use shadcn primitives from src/components/ui/

function ErrorBanner({ message, onClose }: { message: string; onClose: () => void }) {
  return (
    <div
      className="w-full mb-4 rounded-md p-3 flex items-start justify-between"
      style={{ background: 'var(--destructive)', color: 'var(--destructive-foreground)' }}>
      <div className="text-sm">{message}</div>
      <button aria-label="Dismiss error" onClick={onClose} className="ml-4 font-medium">
        ✕
      </button>
    </div>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);

  function validateEmail(value: string): string | null {
    if (!value) return 'Email is required';
    // simple RFC-ish check
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(value)) return 'Enter a valid email';
    return null;
  }

  function validatePassword(value: string): string | null {
    if (!value) return 'Password is required';
    if (value.length < 8) return 'Password must be at least 8 characters';
    return null;
  }

  async function handleSubmit(e?: React.FormEvent) {
    e?.preventDefault();
    const eErr = validateEmail(email);
    const pErr = validatePassword(password);
    setEmailError(eErr);
    setPasswordError(pErr);
    setBanner(null);
    if (eErr || pErr) return;

    setSubmitting(true);
    try {
      const payload: LoginRequest = { username: email, password };
      const res: ApiResult<any> = await login(payload);
      if (!res.ok) {
        setBanner(res.error.message || 'Login failed');
        setSubmitting(false);
        return;
      }
      // success — redirect
      router.push('/dashboard');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ background: 'var(--background)' }}>
      <div className="text-center mb-6">
        <div
          style={{
            color: 'var(--color-accent-foreground)',
            fontSize: 20,
            fontWeight: 600,
          }}>
          Job Agent
        </div>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-[color:var(--foreground)]">
          Sign in
        </h2>
        <p className="text-sm text-[color:var(--color-muted-foreground)] mb-4">
          Sign in to your account
        </p>

        {banner && (
          <ErrorBanner message={banner} onClose={() => setBanner(null)} />
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(v: React.ChangeEvent<HTMLInputElement>) => setEmail(v.target.value)}
              onBlur={() => setEmailError(validateEmail(email))}
              aria-invalid={!!emailError}
            />
            {emailError && (
              <div className="text-sm mt-1 text-[color:var(--destructive-foreground)]">
                {emailError}
              </div>
            )}
          </div>

          <div className="mb-4">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(v: React.ChangeEvent<HTMLInputElement>) => setPassword(v.target.value)}
              onBlur={() => setPasswordError(validatePassword(password))}
              aria-invalid={!!passwordError}
            />
            {passwordError && (
              <div className="text-sm mt-1 text-[color:var(--destructive-foreground)]">
                {passwordError}
              </div>
            )}
          </div>

          <div className="mb-4">
            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? 'Signing in...' : 'Sign in'}
            </Button>
          </div>
        </form>

        <div className="text-center text-sm text-[color:var(--color-muted-foreground)]">
          Don't have an account?{' '}
          <a href="/register" className="text-[color:var(--primary)]">
            Register
          </a>
        </div>
      </Card>
    </div>
  );
}
