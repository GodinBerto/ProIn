# Database

This package is the Python/Django version of the old C# database helper. It
defines the shared table metadata used by the Django backend and points at the
Supabase migration that creates the actual Postgres schema.

The CSV exports were converted into the Supabase migration at:

```text
../../supabase/migrations/20260603014500_create_app_tables_from_csv.sql
```

That migration creates these tables:

- `profiles`
- `organizations`
- `organization_members`
- `organization_invites`
- `documents`
- `document_shares`
- `messages`

The migration also imports the current CSV rows into the matching tables.

To push this database online, link the repo to the correct Supabase project and push:

```powershell
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

Then set the backend database connection string with either `DATABASE_URL`:

```powershell
$env:DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/postgres?sslmode=require"
pnpm --dir apps/backend dev
```

The Django backend also supports the previous .NET-style environment variable:

```powershell
$env:ConnectionStrings__DefaultConnection="Host=YOUR_HOST;Port=5432;Database=postgres;Username=postgres;Password=YOUR_PASSWORD;Ssl Mode=Require"
pnpm --dir apps/backend dev
```
