import { useUserOrg } from "@/query/organizationQuery";
import {
  Building2,
  Check,
  ChevronsUpDown,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Plus,
  User,
} from "@repo/ui";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export function OrgSwitcher() {
  const navigate = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

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
    <DropdownMenu>
      <DropdownMenuTrigger className="flex w-full items-center justify-between gap-2 rounded-md border border-border px-3 py-2 text-left text-sm bg-white hover:bg-surface/70 outline-none min-w-62.5">
        <div className="flex min-w-0 items-center gap-2">
          {currentOrg ? (
            <Building2 className="size-4 shrink-0 text-primary" />
          ) : (
            <User className="size-4 shrink-0 text-muted-foreground" />
          )}
          <span className="truncate font-medium">
            {currentOrg ? currentOrg.slug : "Personal"}
          </span>
        </div>
        <ChevronsUpDown className="size-3 shrink-0 text-muted-foreground" />
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="start">
        <DropdownMenuLabel className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
          Workspace
        </DropdownMenuLabel>
        <DropdownMenuItem onClick={() => navigate.push("/dashboard")}>
          <User className="mr-2 size-4" />
          Personal
          {!currentOrg && <Check className="ml-auto size-3" />}
        </DropdownMenuItem>
        {orgs.length > 0 && <DropdownMenuSeparator />}
        {orgs.map((o) => (
          <DropdownMenuItem
            key={o.id}
            onClick={() =>
              navigate.push(`"/org/$slug", params: { slug: o.slug } `)
            }
          >
            <Building2 className="mr-2 size-4" />
            <span className="truncate">{o.slug}</span>
            {currentOrg?.id === o.id && <Check className="ml-auto size-3" />}
          </DropdownMenuItem>
        ))}
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/orgs/new" className="flex items-center">
            <Plus className="mr-2 size-4" />
            Create organization
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
