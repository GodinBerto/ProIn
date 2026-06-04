from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import dj_database_url


CONNECTION_STRING_ENV_KEYS = (
    "ConnectionStrings__DefaultConnection",
    "CONNECTIONSTRINGS__DEFAULTCONNECTION",
    "DATABASE_URL",
)


def get_connection_string(
    default: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> str | None:
    source = environ or os.environ

    for key in CONNECTION_STRING_ENV_KEYS:
        value = source.get(key)
        if value:
            return value

    return default


def build_django_databases(
    default_url: str,
    *,
    conn_max_age: int = 600,
    supabase_pooler_url_path: Path | None = None,
) -> dict[str, dict]:
    connection_string = get_connection_string(default_url)
    connection_string = use_linked_supabase_pooler(
        connection_string,
        supabase_pooler_url_path=supabase_pooler_url_path,
    )

    return {
        "default": parse_connection_string(
            connection_string,
            conn_max_age=conn_max_age,
        )
    }


def parse_connection_string(connection_string: str, *, conn_max_age: int = 600) -> dict:
    if "://" in connection_string:
        return dj_database_url.parse(connection_string, conn_max_age=conn_max_age)

    values = _parse_key_value_connection_string(connection_string)
    if not values:
        raise ValueError("Database connection string is empty or invalid.")

    options = {}
    ssl_mode = values.get("ssl mode") or values.get("sslmode")
    if ssl_mode:
        options["sslmode"] = ssl_mode.replace(" ", "").lower()

    database = values.get("database") or values.get("dbname") or values.get("db")
    username = values.get("username") or values.get("user") or values.get("uid")
    password = values.get("password") or values.get("pwd")

    return {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": values.get("host", ""),
        "PORT": values.get("port", "5432"),
        "NAME": database or "postgres",
        "USER": username or "postgres",
        "PASSWORD": password or "",
        "CONN_MAX_AGE": conn_max_age,
        "OPTIONS": options,
    }


def use_linked_supabase_pooler(
    connection_string: str,
    *,
    supabase_pooler_url_path: Path | None = None,
) -> str:
    if not supabase_pooler_url_path or "://" not in connection_string:
        return connection_string

    parsed = urlsplit(connection_string)
    host = parsed.hostname or ""
    if not (host.startswith("db.") and host.endswith(".supabase.co")):
        return connection_string

    if not supabase_pooler_url_path.exists():
        return connection_string

    pooler = urlsplit(supabase_pooler_url_path.read_text().strip())
    if not pooler.hostname:
        return connection_string

    username = pooler.username or parsed.username
    password = parsed.password or pooler.password
    netloc = _build_netloc(
        username=username,
        password=password,
        host=pooler.hostname,
        port=pooler.port or parsed.port,
    )

    return urlunsplit(
        (
            parsed.scheme or pooler.scheme,
            netloc,
            parsed.path or pooler.path,
            parsed.query or pooler.query,
            parsed.fragment,
        )
    )


def _parse_key_value_connection_string(connection_string: str) -> dict[str, str]:
    values: dict[str, str] = {}

    for part in connection_string.split(";"):
        if not part.strip() or "=" not in part:
            continue

        key, value = part.split("=", 1)
        values[key.strip().lower()] = value.strip()

    return values


def _build_netloc(
    *,
    username: str | None,
    password: str | None,
    host: str,
    port: int | None,
) -> str:
    userinfo = ""
    if username:
        userinfo = _quote_userinfo(username)
        if password:
            userinfo = f"{userinfo}:{_quote_userinfo(password)}"
        userinfo = f"{userinfo}@"

    suffix = f":{port}" if port else ""
    return f"{userinfo}{host}{suffix}"


def _quote_userinfo(value: str) -> str:
    return quote(unquote(value), safe="")
