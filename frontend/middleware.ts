import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtDecode } from 'jwt-decode'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')
  const { pathname } = request.nextUrl

  // صفحات نیازمند احراز هویت
  const protectedPaths = ['/dashboard']
  const adminPaths = ['/admin']
  const guestPaths = ['/auth/login', '/auth/register']

  // چک کردن دسترسی به صفحات محافظت شده
  if (protectedPaths.some(path => pathname.startsWith(path))) {
    if (!token) {
      return NextResponse.redirect(new URL('/auth/login', request.url))
    }
  }

  // چک کردن دسترسی به پنل ادمین
  if (adminPaths.some(path => pathname.startsWith(path))) {
    if (!token) {
      return NextResponse.redirect(new URL('/auth/login', request.url))
    }
    
    try {
      const decoded = jwtDecode(token.value)
      if (decoded.role !== 'admin') {
        return NextResponse.redirect(new URL('/dashboard', request.url))
      }
    } catch {
      return NextResponse.redirect(new URL('/auth/login', request.url))
    }
  }

  // اگر کاربر لاگین کرده است نباید بتواند به صفحات مهمان برود
  if (guestPaths.some(path => pathname.startsWith(path))) {
    if (token) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/admin/:path*',
    '/auth/:path*',
  ]
} 