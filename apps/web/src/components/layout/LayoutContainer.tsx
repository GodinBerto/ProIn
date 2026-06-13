"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useSearchParams } from "next/navigation";
import {
  FileText,
  LayoutDashboard,
  Settings,
  LogOut,
  Sparkles,
  Users,
  MessageSquare,
  Button,
} from "@repo/ui";
import { useUserStore } from "@/stores/user-store";
import { OrgSwitcher } from "../organizations/OrgSwitcher";
import { useUserOrg } from "@/query/organizationQuery";

const personalItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Documents", url: "/documents", icon: FileText },
  { title: "Settings", url: "/settings", icon: Settings },
];

export default function LayoutContainer({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useUserStore();

  const plan = user?.plan || "free";
  const profileImage = user?.avatar_url || "/profile.jpg";

  const { data: orgs = [] } = useUserOrg();

  const match = pathname.match(/^\/org\/([^/]+)/);
  const currentSlug = match?.[1] ?? null;

  const orgId = searchParams.get("org");

  const currentOrg = currentSlug
    ? orgs.find((o) => o.slug === currentSlug)
    : orgId
      ? orgs.find((o) => o.id === orgId)
      : null;

  return (
    <div className="min-h-screen w-full bg-background text-foreground">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col border-r border-border bg-sidebar p-4 md:flex">
        <Link
          href="/dashboard"
          className="mb-4 flex items-center gap-2 px-2 font-semibold tracking-tight"
        >
          <span className="size-6 rounded bg-primary" />
          <span>ProIn</span>
        </Link>

        <nav className="flex flex-col gap-1">
          {personalItems.map((item) => {
            const active =
              pathname === item.url ||
              (item.url !== "/dashboard" && pathname.startsWith(item.url));

            return (
              <Link
                key={item.url}
                href={item.url}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "bg-surface text-primary"
                    : "text-muted-foreground hover:bg-surface hover:text-foreground"
                }`}
              >
                <item.icon className="size-4" />
                {item.title}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="mt-auto space-y-3">
          <Button
            variant={"outline"}
            className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-surface hover:text-foreground"
          >
            <LogOut className="size-4" /> Sign out
          </Button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex min-h-screen flex-col md:ml-60">
        <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-border bg-background/80 px-6 backdrop-blur">
          <div className="">
            <OrgSwitcher />
          </div>

          <div className="flex items-center gap-3">
            {plan !== "pro" ? (
              <Link
                href="/pricing"
                className="hidden text-xs font-medium text-primary hover:underline md:inline"
              >
                Upgrade
              </Link>
            ) : (
              <div>
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary">
                  Pro
                </span>{" "}
              </div>
            )}

            <Link
              href="/settings"
              className="text-muted-foreground hover:text-foreground rounded-full overflow-hidden "
            >
              <Image
                src={`${profileImage}`}
                alt={"Profile Image"}
                width={30}
                height={30}
              />
            </Link>
          </div>
        </header>

        <div className="flex-1">{children}</div>
      </main>
    </div>
  );
}
