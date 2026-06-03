namespace ProIn.Database;

public sealed class DatabaseTableDefinition
{
    public DatabaseTableDefinition(
        string tableName,
        IReadOnlyList<DatabaseColumn> columns,
        string orderByColumn = "created_at")
    {
        TableName = tableName;
        Columns = columns;
        OrderByColumn = orderByColumn;
        ColumnsByName = columns.ToDictionary(
            column => column.Name,
            StringComparer.OrdinalIgnoreCase);
    }

    public string TableName { get; }

    public IReadOnlyList<DatabaseColumn> Columns { get; }

    public string OrderByColumn { get; }

    public IReadOnlyDictionary<string, DatabaseColumn> ColumnsByName { get; }

    public DatabaseColumn IdColumn => ColumnsByName["id"];
}
