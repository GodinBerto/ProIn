import { getToken } from "next-auth/jwt";
import { NextRequest, NextResponse } from "next/server";

const validRoutes = [
  "/",
  "/dashboard",
  "/products",
  "/login",
  "/register",
  "/auth",
  "/api",
];

const protectedRoutes = ["/dashboard"];
const guestOnlyRoutes = ["/", "/login", "/register"];

export async function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  const routeExists = validRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (!routeExists) {
    return NextResponse.rewrite(new URL("/not-found", request.url));
  }

  const token = await getToken({
    req: request,
    secret: process.env.NEXTAUTH_SECRET,
  });

  const isProtected = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  const isGuestOnly = guestOnlyRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (isProtected && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isGuestOnly && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
