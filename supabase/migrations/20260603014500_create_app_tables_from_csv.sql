create extension if not exists "pgcrypto";

create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists public.profiles (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  full_name text,
  company_name text,
  plan text not null default 'free',
  downloads_used integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  avatar_url text,
  phone text,
  legal_name text,
  tax_id text,
  address_line1 text,
  address_line2 text,
  city text,
  state text,
  postal_code text,
  country text,
  website text,
  logo_url text,
  default_currency text not null default 'USD',
  default_payment_terms text,
  invoice_footer text,
  brand_color text,
  default_template text,
  bank_name text,
  bank_account_name text,
  bank_account_number text,
  bank_swift text,
  paypal_email text,
  notify_on_view boolean not null default true,
  notify_weekly boolean not null default false
);

create table if not exists public.organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  logo_url text,
  owner_id uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.organization_members (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.organizations(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  role text not null default 'member',
  created_at timestamptz not null default now(),
  constraint organization_members_role_check check (role in ('owner', 'admin', 'member')),
  constraint organization_members_org_user_key unique (org_id, user_id)
);

create table if not exists public.organization_invites (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.organizations(id) on delete cascade,
  email text not null,
  role text not null default 'member',
  token text not null unique,
  invited_by uuid references public.profiles(id) on delete set null,
  expires_at timestamptz not null,
  accepted_at timestamptz,
  created_at timestamptz not null default now(),
  constraint organization_invites_role_check check (role in ('owner', 'admin', 'member'))
);

create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  type text not null,
  number text not null,
  title text,
  client_name text,
  data jsonb not null default '{}'::jsonb,
  status text not null,
  is_public boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  org_id uuid references public.organizations(id) on delete set null,
  constraint documents_type_check check (type in ('invoice', 'proposal')),
  constraint documents_status_check check (status in ('draft', 'sent', 'accepted', 'rejected', 'paid', 'unpaid', 'overdue'))
);

create table if not exists public.document_shares (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  org_id uuid references public.organizations(id) on delete cascade,
  shared_with_user_id uuid references public.profiles(id) on delete cascade,
  role text not null default 'viewer',
  created_at timestamptz not null default now(),
  constraint document_shares_role_check check (role in ('viewer', 'editor')),
  constraint document_shares_document_user_key unique (document_id, shared_with_user_id)
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.organizations(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists organizations_owner_id_idx on public.organizations(owner_id);
create index if not exists organization_members_org_id_idx on public.organization_members(org_id);
create index if not exists organization_members_user_id_idx on public.organization_members(user_id);
create index if not exists organization_invites_org_id_idx on public.organization_invites(org_id);
create index if not exists documents_user_id_idx on public.documents(user_id);
create index if not exists documents_org_id_idx on public.documents(org_id);
create index if not exists document_shares_document_id_idx on public.document_shares(document_id);
create index if not exists messages_org_id_idx on public.messages(org_id);

drop trigger if exists profiles_touch_updated_at on public.profiles;
create trigger profiles_touch_updated_at
before update on public.profiles
for each row execute function public.touch_updated_at();

drop trigger if exists organizations_touch_updated_at on public.organizations;
create trigger organizations_touch_updated_at
before update on public.organizations
for each row execute function public.touch_updated_at();

drop trigger if exists documents_touch_updated_at on public.documents;
create trigger documents_touch_updated_at
before update on public.documents
for each row execute function public.touch_updated_at();

alter table public.profiles enable row level security;
alter table public.organizations enable row level security;
alter table public.organization_members enable row level security;
alter table public.organization_invites enable row level security;
alter table public.documents enable row level security;
alter table public.document_shares enable row level security;
alter table public.messages enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
on public.profiles for select
to authenticated
using (id = auth.uid());

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
on public.profiles for update
to authenticated
using (id = auth.uid())
with check (id = auth.uid());

drop policy if exists "organizations_select_members" on public.organizations;
create policy "organizations_select_members"
on public.organizations for select
to authenticated
using (
  owner_id = auth.uid()
  or exists (
    select 1
    from public.organization_members member
    where member.org_id = organizations.id
      and member.user_id = auth.uid()
  )
);

drop policy if exists "organization_members_select_own" on public.organization_members;
create policy "organization_members_select_own"
on public.organization_members for select
to authenticated
using (user_id = auth.uid());

drop policy if exists "documents_select_own_or_public" on public.documents;
create policy "documents_select_own_or_public"
on public.documents for select
to authenticated
using (
  is_public
  or user_id = auth.uid()
  or exists (
    select 1
    from public.organization_members member
    where member.org_id = documents.org_id
      and member.user_id = auth.uid()
  )
);

drop policy if exists "messages_select_org_members" on public.messages;
create policy "messages_select_org_members"
on public.messages for select
to authenticated
using (
  exists (
    select 1
    from public.organization_members member
    where member.org_id = messages.org_id
      and member.user_id = auth.uid()
  )
);

insert into public.profiles (
  id,
  email,
  full_name,
  company_name,
  plan,
  downloads_used,
  created_at,
  updated_at,
  avatar_url,
  phone,
  legal_name,
  tax_id,
  address_line1,
  address_line2,
  city,
  state,
  postal_code,
  country,
  website,
  logo_url,
  default_currency,
  default_payment_terms,
  invoice_footer,
  brand_color,
  default_template,
  bank_name,
  bank_account_name,
  bank_account_number,
  bank_swift,
  paypal_email,
  notify_on_view,
  notify_weekly
) values (
  '28f699d1-2777-409e-8945-db30d953c1be',
  'godfredquarm123@gmail.com',
  'GodinBerto',
  'BertoStudio',
  'pro',
  0,
  '2026-06-01 22:39:46.14543+00',
  '2026-06-02 22:52:11.9877+00',
  null,
  null,
  null,
  null,
  null,
  null,
  null,
  null,
  null,
  null,
  null,
  null,
  'USD',
  'Net 14',
  null,
  '#4f46e5',
  'modern',
  null,
  null,
  null,
  null,
  null,
  true,
  false
)
on conflict (id) do update set
  email = excluded.email,
  full_name = excluded.full_name,
  company_name = excluded.company_name,
  plan = excluded.plan,
  downloads_used = excluded.downloads_used,
  updated_at = excluded.updated_at,
  default_currency = excluded.default_currency,
  default_payment_terms = excluded.default_payment_terms,
  brand_color = excluded.brand_color,
  default_template = excluded.default_template,
  notify_on_view = excluded.notify_on_view,
  notify_weekly = excluded.notify_weekly;

insert into public.organizations (
  id,
  name,
  slug,
  logo_url,
  owner_id,
  created_at,
  updated_at
) values (
  '1fb4c359-a01b-4e22-ad42-b15a0407031a',
  'GodinBerto',
  'godinberto',
  null,
  '28f699d1-2777-409e-8945-db30d953c1be',
  '2026-06-03 00:31:10.644845+00',
  '2026-06-03 00:31:10.644845+00'
)
on conflict (id) do update set
  name = excluded.name,
  slug = excluded.slug,
  logo_url = excluded.logo_url,
  owner_id = excluded.owner_id,
  updated_at = excluded.updated_at;

insert into public.organization_members (
  id,
  org_id,
  user_id,
  role,
  created_at
) values (
  '78ae4504-6e47-4db8-b76f-76e19550ea5a',
  '1fb4c359-a01b-4e22-ad42-b15a0407031a',
  '28f699d1-2777-409e-8945-db30d953c1be',
  'owner',
  '2026-06-03 00:31:10.644845+00'
)
on conflict (id) do update set
  org_id = excluded.org_id,
  user_id = excluded.user_id,
  role = excluded.role;

insert into public.documents (
  id,
  user_id,
  type,
  number,
  title,
  client_name,
  data,
  status,
  is_public,
  created_at,
  updated_at,
  org_id
) values
(
  'f7072389-f1b5-438a-b65b-5536ed4a71a9',
  '28f699d1-2777-409e-8945-db30d953c1be',
  'proposal',
  'PRO-2026-7210',
  'Software Development',
  'BertoStudio',
  $json${"client_name":"BertoStudio","company_name":"","currency":"USD","prepared_by":"BertoStudio","price":3000,"project_description":"We are building you a software product","project_title":"Software Development","scope":"Frontend, Backend, and everything included","timeline":"3 Month"}$json$::jsonb,
  'draft',
  true,
  '2026-06-01 22:44:54.451621+00',
  '2026-06-01 22:44:54.451621+00',
  null
),
(
  '0eee26a2-5c78-41e4-99cb-26be3e2e5923',
  '28f699d1-2777-409e-8945-db30d953c1be',
  'invoice',
  'INV-2026-3735',
  'Invoice for Godfred Quarm',
  'Godfred Quarm',
  $json${"client_email":"godfredquarm123@gmail.com","client_name":"Godfred Quarm","company_name":"BertoStudio","currency":"USD","description":"","due_date":"2026-05-31","items":[{"description":"Deployment","quantity":1,"rate":100}],"notes":"Thank you for your help.","tax_rate":1,"template":"modern"}$json$::jsonb,
  'unpaid',
  true,
  '2026-06-02 22:59:02.393608+00',
  '2026-06-02 22:59:02.393608+00',
  null
)
on conflict (id) do update set
  user_id = excluded.user_id,
  type = excluded.type,
  number = excluded.number,
  title = excluded.title,
  client_name = excluded.client_name,
  data = excluded.data,
  status = excluded.status,
  is_public = excluded.is_public,
  updated_at = excluded.updated_at,
  org_id = excluded.org_id;

insert into public.messages (
  id,
  org_id,
  user_id,
  content,
  created_at
) values (
  'b8e4de5d-106d-443a-8cfc-47aecedede93',
  '1fb4c359-a01b-4e22-ad42-b15a0407031a',
  '28f699d1-2777-409e-8945-db30d953c1be',
  'hello',
  '2026-06-03 00:31:46.544921+00'
)
on conflict (id) do update set
  org_id = excluded.org_id,
  user_id = excluded.user_id,
  content = excluded.content;
