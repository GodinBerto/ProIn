"use client";
import {
  Button,
  Input,
  Label,
  Loader2,
  Logo,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@repo/ui";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signIn } from "next-auth/react";
import { useState } from "react";

export default function LoginPage() {
  const navigate = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [googleBusy, setGoogleBusy] = useState(false);

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="hidden bg-linear-to-br from-primary to-accent p-12 text-primary-foreground md:flex md:flex-col md:justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <div className="flex size-7 items-center justify-center rounded-md bg-white/15 text-white">
            F
          </div>
          FlowForm
        </Link>
        <div>
          <h2 className="text-balance text-3xl font-semibold tracking-tight">
            Invoices and proposals that get you paid.
          </h2>
          <p className="mt-3 max-w-md text-pretty text-sm text-white/80">
            Stop fighting Word templates. Generate, share, and download
            professional documents in seconds.
          </p>
        </div>
        <div className="text-xs text-white/60">
          Trusted by freelancers worldwide
        </div>
      </div>

      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <Link
            href="/"
            className="mb-8 flex items-center gap-2 font-semibold md:hidden"
          >
            <Logo /> FlowForm
          </Link>
          <h1 className="text-2xl font-semibold tracking-tight">
            Sign in to FlowForm
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Welcome back. Sign in to continue.
          </p>

          <Button
            type="button"
            variant="outline"
            disabled={googleBusy}
            className="mt-6 w-full flex gap-4 items-center px-6 py-3 hover:bg-primary hover:text-white"
            onClick={() => {
              signIn("google");
            }}
          >
            {googleBusy ? (
              <Loader2 className="mr-2 size-4 animate-spin" />
            ) : (
              <svg
                className="mr-2 size-4"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.25 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.1A6.99 6.99 0 0 1 5.47 12c0-.73.13-1.44.36-2.1V7.06H2.18A11 11 0 0 0 1 12c0 1.77.42 3.45 1.18 4.94l3.66-2.84z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"
                />
              </svg>
            )}
            Continue with Google
          </Button>

          <div className="my-6 flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            <div className="h-px flex-1 bg-border" /> or{" "}
            <div className="h-px flex-1 bg-border" />
          </div>

          <Tabs defaultValue="password">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="password">Password</TabsTrigger>
              <TabsTrigger value="magic">Magic link</TabsTrigger>
            </TabsList>

            <TabsContent value="password">
              <form onSubmit={(e) => {}} className="mt-6 space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@studio.com"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                </div>
                <Button type="submit" disabled={busy} className="w-full">
                  {busy && <Loader2 className="mr-2 size-4 animate-spin" />}
                  Sign in
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  disabled={busy}
                  className="w-full"
                  onClick={(e) => {}}
                >
                  Create account
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="magic">
              <form onSubmit={() => {}} className="mt-6 space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="email2">Email</Label>
                  <Input
                    id="email2"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@studio.com"
                  />
                </div>
                <Button type="submit" disabled={busy} className="w-full">
                  {busy && <Loader2 className="mr-2 size-4 animate-spin" />}
                  Send magic link
                </Button>
                <p className="text-center text-xs text-muted-foreground">
                  We'll email you a link to sign in instantly.
                </p>
              </form>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
