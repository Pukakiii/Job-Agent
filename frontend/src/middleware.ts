import { acceptClientHintsHeader } from "@teispace/next-themes/server"
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const PROTECTED = ["/dashboard"]
const AUTH_COOKIE = "fastapiusersauth"

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isProtected = PROTECTED.some((path) => pathname.startsWith(path))

  let response: NextResponse

  if (isProtected) {
    const token = request.cookies.get(AUTH_COOKIE)
    if (!token) {
      const loginUrl = new URL("/login", request.url)
      loginUrl.searchParams.set("from", pathname)
      response = NextResponse.redirect(loginUrl)
    } else {
      response = NextResponse.next()
    }
  } else {
    response = NextResponse.next()
  }

  response.headers.set("Accept-CH", acceptClientHintsHeader())

  return response
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|mockServiceWorker.js|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
