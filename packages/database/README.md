# Database

The CSV exports in this folder have been converted into the Supabase migration at:

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

Then set the backend database connection string:

```powershell
$env:ConnectionStrings__DefaultConnection="Host=YOUR_HOST;Port=5432;Database=postgres;Username=postgres;Password=YOUR_PASSWORD;Ssl Mode=Require;Trust Server Certificate=true"
pnpm --dir apps/backend dev
```
