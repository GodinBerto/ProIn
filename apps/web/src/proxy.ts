import { NextRequest, NextResponse } from "next/server";

// Allow known routes
const validRoutes = ["/", "/dashboard", "/products", "/login", "/register"];

export async function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  const routeExists = validRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (!routeExists) {
    return NextResponse.rewrite(new URL("/not-found", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
