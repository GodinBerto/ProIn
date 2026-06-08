"use client";
import Link from "next/link";
import Header from "../../components/header";
import { Button } from "@repo/ui";
import Footer from "../../components/footer";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1 flex-col items-center justify-center gap-6">
        <h1 className="text-4xl font-bold">404 - Page Not Found</h1>
        <p className="text-lg text-muted-foreground">
          Oops! The page you're looking for doesn't exist.
        </p>
        <Button variant="default" className="px-6 py-3">
          <Link href="/">Go back home</Link>
        </Button>
      </div>
      <Footer />
    </div>
  );
}
