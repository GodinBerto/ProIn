from django.core.exceptions import ValidationError
from django.db import DataError, DatabaseError, IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError


def create_crud_router(model, schema, table):
    router = Router()

    @router.get("", response=list[schema])
    def list_items(request, limit: int = 100, offset: int = 0):
        limit = max(1, min(limit, 500))
        offset = max(0, offset)
        return model.objects.all().order_by(f'-{table.order_by_column}')[offset:offset+limit]

    @router.get("/{id}", response=schema)
    def get_item(request, id: str):
        return get_object_or_404(model, id=id)

    @router.post("", response=schema)
    def create_item(request, payload: dict):
        clean_payload = clean_payload_for_table(table, payload, mode="create")
        try:
            return model.objects.create(**clean_payload)
        except (DataError, IntegrityError, ValidationError) as exc:
            raise HttpError(400, str(exc)) from exc
        except DatabaseError as exc:
            raise HttpError(503, str(exc)) from exc

    @router.put("/{id}", response=schema)
    def update_item(request, id: str, payload: dict):
        obj = get_object_or_404(model, id=id)
        clean_payload = clean_payload_for_table(table, payload, mode="update")
        try:
            for attr, value in clean_payload.items():
                setattr(obj, attr, value)
            obj.save()
            return obj
        except (DataError, IntegrityError, ValidationError) as exc:
            raise HttpError(400, str(exc)) from exc
        except DatabaseError as exc:
            raise HttpError(503, str(exc)) from exc

    @router.delete("/{id}")
    def delete_item(request, id: str):
        obj = get_object_or_404(model, id=id)
        obj.delete()
        return {"success": True}

    return router


def clean_payload_for_table(table, payload: dict, *, mode: str) -> dict:
    allowed_columns = (
        table.create_column_names if mode == "create" else table.update_column_names
    )
    payload_columns = set(payload)
    unknown_columns = sorted(payload_columns - table.column_names)
    blocked_columns = sorted((payload_columns & table.column_names) - allowed_columns)

    if unknown_columns:
        raise HttpError(
            400,
            f"Unknown columns for {table.table_name}: {', '.join(unknown_columns)}",
        )

    if blocked_columns:
        raise HttpError(
            400,
            f"Columns cannot be {mode}d for {table.table_name}: {', '.join(blocked_columns)}",
        )

    return {
        column: value
        for column, value in payload.items()
        if column in allowed_columns
    }
