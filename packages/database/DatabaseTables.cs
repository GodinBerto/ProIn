namespace ProIn.Database;

public static class DatabaseTables
{
    public static readonly DatabaseTableDefinition Profiles = new(
        "profiles",
        [
            Id(),
            Text("email"),
            Text("full_name"),
            Text("company_name"),
            Text("plan"),
            Integer("downloads_used"),
            Timestamp("created_at", allowUpdate: false),
            Timestamp("updated_at", allowCreate: false, allowUpdate: false),
            Text("avatar_url"),
            Text("phone"),
            Text("legal_name"),
            Text("tax_id"),
            Text("address_line1"),
            Text("address_line2"),
            Text("city"),
            Text("state"),
            Text("postal_code"),
            Text("country"),
            Text("website"),
            Text("logo_url"),
            Text("default_currency"),
            Text("default_payment_terms"),
            Text("invoice_footer"),
            Text("brand_color"),
            Text("default_template"),
            Text("bank_name"),
            Text("bank_account_name"),
            Text("bank_account_number"),
            Text("bank_swift"),
            Text("paypal_email"),
            Boolean("notify_on_view"),
            Boolean("notify_weekly")
        ]);

    public static readonly DatabaseTableDefinition Organizations = new(
        "organizations",
        [
            Id(),
            Text("name"),
            Text("slug"),
            Text("logo_url"),
            Uuid("owner_id"),
            Timestamp("created_at", allowUpdate: false),
            Timestamp("updated_at", allowCreate: false, allowUpdate: false)
        ]);

    public static readonly DatabaseTableDefinition OrganizationMembers = new(
        "organization_members",
        [
            Id(),
            Uuid("org_id"),
            Uuid("user_id"),
            Text("role"),
            Timestamp("created_at", allowUpdate: false)
        ]);

    public static readonly DatabaseTableDefinition OrganizationInvites = new(
        "organization_invites",
        [
            Id(),
            Uuid("org_id"),
            Text("email"),
            Text("role"),
            Text("token"),
            Uuid("invited_by"),
            Timestamp("expires_at"),
            Timestamp("accepted_at"),
            Timestamp("created_at", allowUpdate: false)
        ]);

    public static readonly DatabaseTableDefinition Documents = new(
        "documents",
        [
            Id(),
            Uuid("user_id"),
            Text("type"),
            Text("number"),
            Text("title"),
            Text("client_name"),
            Jsonb("data"),
            Text("status"),
            Boolean("is_public"),
            Timestamp("created_at", allowUpdate: false),
            Timestamp("updated_at", allowCreate: false, allowUpdate: false),
            Uuid("org_id")
        ]);

    public static readonly DatabaseTableDefinition DocumentShares = new(
        "document_shares",
        [
            Id(),
            Uuid("document_id"),
            Uuid("org_id"),
            Uuid("shared_with_user_id"),
            Text("role"),
            Timestamp("created_at", allowUpdate: false)
        ]);

    public static readonly DatabaseTableDefinition Messages = new(
        "messages",
        [
            Id(),
            Uuid("org_id"),
            Uuid("user_id"),
            Text("content"),
            Timestamp("created_at", allowUpdate: false)
        ]);

    private static DatabaseColumn Id() => Uuid("id", allowUpdate: false);

    private static DatabaseColumn Text(
        string name,
        bool allowCreate = true,
        bool allowUpdate = true) => new(name, DatabaseColumnType.Text, allowCreate, allowUpdate);

    private static DatabaseColumn Uuid(
        string name,
        bool allowCreate = true,
        bool allowUpdate = true) => new(name, DatabaseColumnType.Uuid, allowCreate, allowUpdate);

    private static DatabaseColumn Integer(
        string name,
        bool allowCreate = true,
        bool allowUpdate = true) => new(name, DatabaseColumnType.Integer, allowCreate, allowUpdate);

    private static DatabaseColumn Boolean(
        string name,
        bool allowCreate = true,
        bool allowUpdate = true) => new(name, DatabaseColumnType.Boolean, allowCreate, allowUpdate);

    private static DatabaseColumn Timestamp(
        string name,
        bool allowCreate = true,
        bool allowUpdate = true) => new(name, DatabaseColumnType.Timestamp, allowCreate, allowUpdate);

    private static DatabaseColumn Jsonb(
        string name,
        bool allowCreate = true,
        bool allowUpdate = true) => new(name, DatabaseColumnType.Jsonb, allowCreate, allowUpdate);
}
