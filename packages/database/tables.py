from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DatabaseColumnType(str, Enum):
    TEXT = "text"
    UUID = "uuid"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"
    JSONB = "jsonb"


@dataclass(frozen=True)
class DatabaseColumn:
    name: str
    type: DatabaseColumnType
    allow_create: bool = True
    allow_update: bool = True


@dataclass(frozen=True)
class DatabaseTableDefinition:
    table_name: str
    columns: tuple[DatabaseColumn, ...]
    order_by_column: str = "created_at"

    @property
    def columns_by_name(self) -> dict[str, DatabaseColumn]:
        return {column.name.lower(): column for column in self.columns}

    @property
    def column_names(self) -> frozenset[str]:
        return frozenset(column.name for column in self.columns)

    @property
    def create_column_names(self) -> frozenset[str]:
        return frozenset(
            column.name for column in self.columns if column.allow_create
        )

    @property
    def update_column_names(self) -> frozenset[str]:
        return frozenset(
            column.name for column in self.columns if column.allow_update
        )

    @property
    def id_column(self) -> DatabaseColumn:
        return self.columns_by_name["id"]


def _id() -> DatabaseColumn:
    return _uuid("id", allow_update=False)


def _text(
    name: str,
    *,
    allow_create: bool = True,
    allow_update: bool = True,
) -> DatabaseColumn:
    return DatabaseColumn(name, DatabaseColumnType.TEXT, allow_create, allow_update)


def _uuid(
    name: str,
    *,
    allow_create: bool = True,
    allow_update: bool = True,
) -> DatabaseColumn:
    return DatabaseColumn(name, DatabaseColumnType.UUID, allow_create, allow_update)


def _integer(
    name: str,
    *,
    allow_create: bool = True,
    allow_update: bool = True,
) -> DatabaseColumn:
    return DatabaseColumn(
        name,
        DatabaseColumnType.INTEGER,
        allow_create,
        allow_update,
    )


def _boolean(
    name: str,
    *,
    allow_create: bool = True,
    allow_update: bool = True,
) -> DatabaseColumn:
    return DatabaseColumn(
        name,
        DatabaseColumnType.BOOLEAN,
        allow_create,
        allow_update,
    )


def _timestamp(
    name: str,
    *,
    allow_create: bool = True,
    allow_update: bool = True,
) -> DatabaseColumn:
    return DatabaseColumn(
        name,
        DatabaseColumnType.TIMESTAMP,
        allow_create,
        allow_update,
    )


def _jsonb(
    name: str,
    *,
    allow_create: bool = True,
    allow_update: bool = True,
) -> DatabaseColumn:
    return DatabaseColumn(name, DatabaseColumnType.JSONB, allow_create, allow_update)


class DatabaseTables:
    PROFILES = DatabaseTableDefinition(
        "profiles",
        (
            _id(),
            _text("email"),
            _text("full_name"),
            _text("company_name"),
            _text("plan"),
            _integer("downloads_used"),
            _timestamp("created_at", allow_update=False),
            _timestamp("updated_at", allow_create=False, allow_update=False),
            _text("avatar_url"),
            _text("phone"),
            _text("legal_name"),
            _text("tax_id"),
            _text("address_line1"),
            _text("address_line2"),
            _text("city"),
            _text("state"),
            _text("postal_code"),
            _text("country"),
            _text("website"),
            _text("logo_url"),
            _text("default_currency"),
            _text("default_payment_terms"),
            _text("invoice_footer"),
            _text("brand_color"),
            _text("default_template"),
            _text("bank_name"),
            _text("bank_account_name"),
            _text("bank_account_number"),
            _text("bank_swift"),
            _text("paypal_email"),
            _boolean("notify_on_view"),
            _boolean("notify_weekly"),
        ),
    )

    ORGANIZATIONS = DatabaseTableDefinition(
        "organizations",
        (
            _id(),
            _text("name"),
            _text("slug"),
            _text("logo_url"),
            _uuid("owner_id"),
            _timestamp("created_at", allow_update=False),
            _timestamp("updated_at", allow_create=False, allow_update=False),
        ),
    )

    ORGANIZATION_MEMBERS = DatabaseTableDefinition(
        "organization_members",
        (
            _id(),
            _uuid("org_id"),
            _uuid("user_id"),
            _text("role"),
            _timestamp("created_at", allow_update=False),
        ),
    )

    ORGANIZATION_INVITES = DatabaseTableDefinition(
        "organization_invites",
        (
            _id(),
            _uuid("org_id"),
            _text("email"),
            _text("role"),
            _text("token"),
            _uuid("invited_by"),
            _timestamp("expires_at"),
            _timestamp("accepted_at"),
            _timestamp("created_at", allow_update=False),
        ),
    )

    DOCUMENTS = DatabaseTableDefinition(
        "documents",
        (
            _id(),
            _uuid("user_id"),
            _text("type"),
            _text("number"),
            _text("title"),
            _text("client_name"),
            _jsonb("data"),
            _text("status"),
            _boolean("is_public"),
            _timestamp("created_at", allow_update=False),
            _timestamp("updated_at", allow_create=False, allow_update=False),
            _uuid("org_id"),
        ),
    )

    DOCUMENT_SHARES = DatabaseTableDefinition(
        "document_shares",
        (
            _id(),
            _uuid("document_id"),
            _uuid("org_id"),
            _uuid("shared_with_user_id"),
            _text("role"),
            _timestamp("created_at", allow_update=False),
        ),
    )

    MESSAGES = DatabaseTableDefinition(
        "messages",
        (
            _id(),
            _uuid("org_id"),
            _uuid("user_id"),
            _text("content"),
            _timestamp("created_at", allow_update=False),
        ),
    )

    ALL = (
        PROFILES,
        ORGANIZATIONS,
        ORGANIZATION_MEMBERS,
        ORGANIZATION_INVITES,
        DOCUMENTS,
        DOCUMENT_SHARES,
        MESSAGES,
    )

    BY_NAME = {table.table_name: table for table in ALL}
