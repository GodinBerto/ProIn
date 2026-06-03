namespace ProIn.Database;

public sealed record DatabaseColumn(
    string Name,
    DatabaseColumnType Type,
    bool AllowCreate = true,
    bool AllowUpdate = true);

public enum DatabaseColumnType
{
    Text,
    Uuid,
    Integer,
    Boolean,
    Timestamp,
    Jsonb
}
