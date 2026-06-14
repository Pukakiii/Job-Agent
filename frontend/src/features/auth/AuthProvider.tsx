"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"

import {
  getMe,
  login as authLogin,
  logout as authLogout,
  type LoginRequest,
  type User,
} from "@/lib/api/auth"
import type { ApiResult } from "@/lib/api/client"

export type AuthContextValue = {
  user: User | null
  loading: boolean
  login: (credentials: LoginRequest) => Promise<ApiResult<User>>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider")
  }
  return context
}

type AuthProviderProps = {
  children: ReactNode
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    const result = await getMe()
    if (result.ok) {
      setUser(result.data)
    } else {
      setUser(null)
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const login = useCallback(
    async (credentials: LoginRequest): Promise<ApiResult<User>> => {
      const result = await authLogin(credentials)
      if (result.ok) {
        await refresh()
      }
      return result
    },
    [refresh],
  )

  const logout = useCallback(async () => {
    await authLogout()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, logout, refresh }),
    [user, loading, login, logout, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
