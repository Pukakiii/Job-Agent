import type { User } from "@/lib/api/auth"

export const userMe: User = {
  id: "usr_001",
  email: "test@example.com",
  is_active: true,
  is_verified: true,
  is_superuser: false,
}