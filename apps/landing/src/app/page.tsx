"use client";

import {
  ArrowRight,
  Button,
  Check,
  FileText,
  Shield,
  Sparkles,
  Zap,
} from "@repo/ui";
import Link from "next/link";
import Header from "../components/header";
import Footer from "../components/footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div className="pointer-events-none absolute inset-x-0 -top-32 -z-10 mx-auto h-72 max-w-3xl rounded-full bg-primary/20 blur-3xl" />
          <div className="mx-auto max-w-4xl px-6 pb-20 pt-20 text-center md:pt-28">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium text-muted-foreground">
              <Sparkles className="size-3.5 text-primary" />
              Built for freelancers
            </div>
            <h1 className="text-balance text-4xl font-semibold tracking-tight md:text-6xl">
              Invoices and proposals,{" "}
              <span className="bg-linear-to-r from-primary to-accent bg-clip-text text-transparent">
                generated in seconds
              </span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-pretty text-base text-muted-foreground md:text-lg">
              Fill out a short form. Get a clean, professional PDF you can share
              or download. No design skills required.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Link href="http://localhost:3005/login">
                <Button
                  size="lg"
                  className="shadow-(--shadow-primary) px-6 py-3"
                >
                  Create your first invoice{" "}
                  <ArrowRight className="ml-1 size-4" />
                </Button>
              </Link>
              <a href="#features">
                <Button size="lg" variant="outline" className="px-6 py-3">
                  See how it works
                </Button>
              </a>
            </div>
            <p className="mt-3 text-xs text-muted-foreground">
              Free plan • 3 PDF downloads • No credit card
            </p>
          </div>

          {/* Preview card */}
          <div className="mx-auto -mt-4 max-w-5xl px-6 pb-20">
            <div className="rounded-2xl border border-border bg-surface p-2 shadow-(--shadow-elev)">
              <div className="rounded-xl bg-background p-8 md:p-12">
                <div className="grid gap-8 md:grid-cols-2">
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                      Invoice
                    </div>
                    <div className="font-mono text-sm">#INV-2026-0042</div>
                    <div className="mt-8">
                      <div className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        Bill to
                      </div>
                      <div className="mt-1 font-medium">Acme Corp Inc.</div>
                      <div className="text-sm text-muted-foreground">
                        contact@acmecorp.com
                      </div>
                    </div>
                  </div>
                  <div className="md:text-right">
                    <div className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                      Total
                    </div>
                    <div className="text-3xl font-semibold tracking-tight text-primary">
                      $2,500.00
                    </div>
                    <div className="mt-8 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                      Due
                    </div>
                    <div className="text-sm font-medium">Jun 30, 2026</div>
                  </div>
                </div>
                <div className="mt-8 border-t border-border pt-6">
                  <div className="flex items-center justify-between text-sm">
                    <span>Brand identity redesign</span>
                    <span className="font-medium">$2,500.00</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="border-t border-border bg-surface/50">
          <div className="mx-auto max-w-6xl px-6 py-20">
            <div className="mb-12 text-center">
              <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">
                Everything you need to look professional
              </h2>
              <p className="mt-3 text-muted-foreground">
                No bloat. Just the essentials, done well.
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              {[
                {
                  i: Zap,
                  t: "Fast generation",
                  d: "Fill out a form, get a polished PDF in seconds. No fiddling with layouts.",
                },
                {
                  i: FileText,
                  t: "Invoices & proposals",
                  d: "Two document types covering 90% of freelance paperwork.",
                },
                {
                  i: Shield,
                  t: "Shareable links",
                  d: "Send a link to your client. No sign-up needed on their side.",
                },
              ].map(({ i: Icon, t, d }) => (
                <div
                  key={t}
                  className="rounded-2xl border border-border bg-background p-6"
                >
                  <div className="mb-4 flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="size-5" />
                  </div>
                  <h3 className="text-sm font-semibold">{t}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section id="pricing" className="border-t border-border">
          <div className="mx-auto max-w-5xl px-6 py-20">
            <div className="mb-12 text-center">
              <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">
                Simple pricing
              </h2>
              <p className="mt-3 text-muted-foreground">
                Start free. Upgrade when you need more.
              </p>
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              <div className="rounded-2xl border border-border bg-background p-8">
                <div className="text-sm font-semibold text-muted-foreground">
                  Free
                </div>
                <div className="mt-2 text-4xl font-semibold tracking-tight">
                  $0
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  For trying it out.
                </p>
                <ul className="mt-6 space-y-2 text-sm">
                  {[
                    "3 PDF downloads total",
                    "Unlimited drafts",
                    "Shareable links",
                    "Watermarked PDFs",
                  ].map((f) => (
                    <li key={f} className="flex items-center gap-2">
                      <Check className="size-4 text-primary" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link href="http://localhost:3005/login" className="mt-8 block">
                  <Button
                    variant="outline"
                    className="w-full px-6 py-3 hover:bg-primary hover:text-primary-foreground duration-200 transition-colors"
                  >
                    Get started
                  </Button>
                </Link>
              </div>
              <div className="relative rounded-2xl border-2 border-primary bg-background p-8 shadow-(--shadow-primary)">
                <div className="absolute -top-3 left-8 rounded-full bg-primary px-3 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary-foreground">
                  Pro
                </div>
                <div className="text-sm font-semibold text-primary">Pro</div>
                <div className="mt-2 text-4xl font-semibold tracking-tight">
                  $12
                  <span className="text-base font-normal text-muted-foreground">
                    /mo
                  </span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  For working freelancers.
                </p>
                <ul className="mt-6 space-y-2 text-sm">
                  {[
                    "Unlimited PDF downloads",
                    "No watermark",
                    "Premium templates",
                    "Priority support",
                  ].map((f) => (
                    <li key={f} className="flex items-center gap-2">
                      <Check className="size-4 text-primary" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link href="http://localhost:3005/login" className="mt-8 block">
                  <Button className="w-full px-6 py-3">Start free trial</Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
