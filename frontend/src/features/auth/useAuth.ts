"use client"

import { useAuthContext } from "./AuthProvider"

export function useAuth() {
  return useAuthContext()
}

export function useUser() {
  const { user, loading } = useAuthContext()
  return { user, loading }
}

export function useIsAuthenticated() {
  const { user, loading } = useAuthContext()
  return { isAuthenticated: !!user, loading }
}
