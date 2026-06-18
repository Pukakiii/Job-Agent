import { describe, expect, it } from "vitest"

import {
  validateConfirmPassword,
  validateEmail,
  validatePassword,
} from "./auth"

describe("validateEmail", () => {
  it("requires a value", () => {
    expect(validateEmail("")).toBe("Email is required")
  })

  it("rejects invalid format", () => {
    expect(validateEmail("not-an-email")).toBe("Enter a valid email")
    expect(validateEmail("missing@domain")).toBe("Enter a valid email")
  })

  it("accepts valid email", () => {
    expect(validateEmail("alice@test.io")).toBeUndefined()
  })
})

describe("validatePassword", () => {
  it("requires a value", () => {
    expect(validatePassword("")).toBe("Password is required")
  })

  it("rejects passwords shorter than 8 characters", () => {
    expect(validatePassword("short")).toBe(
      "Password must be at least 8 characters",
    )
  })

  it("accepts valid password", () => {
    expect(validatePassword("supersecret123")).toBeUndefined()
  })
})

describe("validateConfirmPassword", () => {
  it("requires confirmation", () => {
    expect(validateConfirmPassword("password123", "")).toBe(
      "Please confirm your password",
    )
  })

  it("rejects mismatch", () => {
    expect(validateConfirmPassword("password123", "different")).toBe(
      "Passwords do not match",
    )
  })

  it("accepts matching passwords", () => {
    expect(
      validateConfirmPassword("password123", "password123"),
    ).toBeUndefined()
  })
})
