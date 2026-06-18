export function validateEmail(value: string): string | undefined {
  if (!value) return "Email is required"
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return "Enter a valid email"
}

export function validatePassword(value: string): string | undefined {
  if (!value) return "Password is required"
  if (value.length < 8) return "Password must be at least 8 characters"
}

export function validateConfirmPassword(
  password: string,
  confirmPassword: string,
): string | undefined {
  if (!confirmPassword) return "Please confirm your password"
  if (confirmPassword !== password) return "Passwords do not match"
}
