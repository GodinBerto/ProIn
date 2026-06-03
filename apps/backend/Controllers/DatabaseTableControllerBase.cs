namespace ProIn.Backend.Controllers;

using System.Globalization;
using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.AspNetCore.Mvc;
using Npgsql;
using NpgsqlTypes;

public abstract class DatabaseTableControllerBase(
    AppDatabase database,
    DatabaseTableDefinition table) : ApiControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IReadOnlyList<IReadOnlyDictionary<string, object?>>>> List(
        [FromQuery] int limit = 100,
        [FromQuery] int offset = 0,
        CancellationToken cancellationToken = default)
    {
        limit = Math.Clamp(limit, 1, 500);
        offset = Math.Max(offset, 0);

        try
        {
            await using var connection = await database.OpenConnectionAsync(cancellationToken);
            await using var command = connection.CreateCommand();
            command.CommandText = $"""
                select {SelectColumns()}
                from {QualifiedTableName()}
                order by {Quote(table.OrderByColumn)} desc
                limit @limit offset @offset
                """;
            command.Parameters.Add(new NpgsqlParameter<int>("limit", limit));
            command.Parameters.Add(new NpgsqlParameter<int>("offset", offset));

            await using var reader = await command.ExecuteReaderAsync(cancellationToken);
            return Ok(await ReadRowsAsync(reader, cancellationToken));
        }
        catch (InvalidOperationException ex)
        {
            return DatabaseNotConfigured(ex);
        }
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<IReadOnlyDictionary<string, object?>>> GetById(
        Guid id,
        CancellationToken cancellationToken)
    {
        try
        {
            await using var connection = await database.OpenConnectionAsync(cancellationToken);
            await using var command = connection.CreateCommand();
            command.CommandText = $"""
                select {SelectColumns()}
                from {QualifiedTableName()}
                where id = @id
                limit 1
                """;
            command.Parameters.Add(CreateValueParameter("id", table.IdColumn, id));

            await using var reader = await command.ExecuteReaderAsync(cancellationToken);
            var rows = await ReadRowsAsync(reader, cancellationToken);

            return rows.Count == 0 ? NotFound() : Ok(rows[0]);
        }
        catch (InvalidOperationException ex)
        {
            return DatabaseNotConfigured(ex);
        }
    }

    [HttpPost]
    public async Task<ActionResult<IReadOnlyDictionary<string, object?>>> Create(
        [FromBody] JsonObject payload,
        CancellationToken cancellationToken)
    {
        var columns = GetPayloadColumns(payload, column => column.AllowCreate);

        if (columns.Count == 0)
        {
            return BadRequest(new DatabaseErrorResponse("Request body does not contain any writable columns."));
        }

        try
        {
            await using var connection = await database.OpenConnectionAsync(cancellationToken);
            await using var command = connection.CreateCommand();

            for (var i = 0; i < columns.Count; i++)
            {
                command.Parameters.Add(CreateJsonParameter($"p{i}", columns[i], payload[columns[i].Name]));
            }

            command.CommandText = $"""
                insert into {QualifiedTableName()} ({string.Join(", ", columns.Select(column => Quote(column.Name)))})
                values ({string.Join(", ", Enumerable.Range(0, columns.Count).Select(index => $"@p{index}"))})
                returning {SelectColumns()}
                """;

            await using var reader = await command.ExecuteReaderAsync(cancellationToken);
            var rows = await ReadRowsAsync(reader, cancellationToken);

            return CreatedAtAction(nameof(GetById), new { id = rows[0]["id"] }, rows[0]);
        }
        catch (InvalidOperationException ex)
        {
            return DatabaseNotConfigured(ex);
        }
        catch (PostgresException ex)
        {
            return DatabaseWriteError(ex);
        }
    }

    [HttpPut("{id:guid}")]
    public async Task<ActionResult<IReadOnlyDictionary<string, object?>>> Update(
        Guid id,
        [FromBody] JsonObject payload,
        CancellationToken cancellationToken)
    {
        var columns = GetPayloadColumns(payload, column => column.AllowUpdate && !column.Name.Equals("id", StringComparison.OrdinalIgnoreCase));

        if (columns.Count == 0)
        {
            return BadRequest(new DatabaseErrorResponse("Request body does not contain any writable columns."));
        }

        try
        {
            await using var connection = await database.OpenConnectionAsync(cancellationToken);
            await using var command = connection.CreateCommand();

            command.Parameters.Add(CreateValueParameter("id", table.IdColumn, id));
            for (var i = 0; i < columns.Count; i++)
            {
                command.Parameters.Add(CreateJsonParameter($"p{i}", columns[i], payload[columns[i].Name]));
            }

            command.CommandText = $"""
                update {QualifiedTableName()}
                set {string.Join(", ", columns.Select((column, index) => $"{Quote(column.Name)} = @p{index}"))}
                where id = @id
                returning {SelectColumns()}
                """;

            await using var reader = await command.ExecuteReaderAsync(cancellationToken);
            var rows = await ReadRowsAsync(reader, cancellationToken);

            return rows.Count == 0 ? NotFound() : Ok(rows[0]);
        }
        catch (InvalidOperationException ex)
        {
            return DatabaseNotConfigured(ex);
        }
        catch (PostgresException ex)
        {
            return DatabaseWriteError(ex);
        }
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            await using var connection = await database.OpenConnectionAsync(cancellationToken);
            await using var command = connection.CreateCommand();
            command.CommandText = $"""
                delete from {QualifiedTableName()}
                where id = @id
                returning id
                """;
            command.Parameters.Add(CreateValueParameter("id", table.IdColumn, id));

            var deletedId = await command.ExecuteScalarAsync(cancellationToken);

            return deletedId is null ? NotFound() : NoContent();
        }
        catch (InvalidOperationException ex)
        {
            return DatabaseNotConfigured(ex);
        }
        catch (PostgresException ex)
        {
            return DatabaseWriteError(ex);
        }
    }

    private ActionResult DatabaseNotConfigured(InvalidOperationException ex)
    {
        return StatusCode(
            StatusCodes.Status503ServiceUnavailable,
            new DatabaseErrorResponse(ex.Message));
    }

    private ActionResult DatabaseWriteError(PostgresException ex)
    {
        return BadRequest(new DatabaseErrorResponse(ex.MessageText));
    }

    private List<DatabaseColumn> GetPayloadColumns(
        JsonObject payload,
        Func<DatabaseColumn, bool> filter)
    {
        return payload
            .Select(property => table.ColumnsByName.TryGetValue(property.Key, out var column) ? column : null)
            .Where(column => column is not null && filter(column))
            .Cast<DatabaseColumn>()
            .ToList();
    }

    private async Task<List<IReadOnlyDictionary<string, object?>>> ReadRowsAsync(
        NpgsqlDataReader reader,
        CancellationToken cancellationToken)
    {
        var rows = new List<IReadOnlyDictionary<string, object?>>();

        while (await reader.ReadAsync(cancellationToken))
        {
            var row = new Dictionary<string, object?>(StringComparer.OrdinalIgnoreCase);

            for (var index = 0; index < table.Columns.Count; index++)
            {
                var column = table.Columns[index];
                row[column.Name] = reader.IsDBNull(index)
                    ? null
                    : ReadColumnValue(reader, index, column);
            }

            rows.Add(row);
        }

        return rows;
    }

    private static object? ReadColumnValue(NpgsqlDataReader reader, int index, DatabaseColumn column)
    {
        return column.Type switch
        {
            DatabaseColumnType.Jsonb => JsonNode.Parse(reader.GetString(index)),
            DatabaseColumnType.Timestamp => ReadTimestamp(reader.GetValue(index)),
            _ => reader.GetValue(index)
        };
    }

    private static object ReadTimestamp(object value)
    {
        return value switch
        {
            DateTimeOffset timestamp => timestamp,
            DateTime timestamp => DateTime.SpecifyKind(timestamp, DateTimeKind.Utc),
            _ => value
        };
    }

    private static NpgsqlParameter CreateJsonParameter(
        string name,
        DatabaseColumn column,
        JsonNode? value)
    {
        return CreateParameter(name, column, ConvertJsonValue(column, value));
    }

    private static NpgsqlParameter CreateValueParameter(
        string name,
        DatabaseColumn column,
        object value)
    {
        return CreateParameter(name, column, value);
    }

    private static NpgsqlParameter CreateParameter(
        string name,
        DatabaseColumn column,
        object? value)
    {
        var parameter = new NpgsqlParameter(name, value ?? DBNull.Value)
        {
            NpgsqlDbType = column.Type switch
            {
                DatabaseColumnType.Boolean => NpgsqlDbType.Boolean,
                DatabaseColumnType.Integer => NpgsqlDbType.Integer,
                DatabaseColumnType.Jsonb => NpgsqlDbType.Jsonb,
                DatabaseColumnType.Timestamp => NpgsqlDbType.TimestampTz,
                DatabaseColumnType.Uuid => NpgsqlDbType.Uuid,
                _ => NpgsqlDbType.Text
            }
        };

        return parameter;
    }

    private static object? ConvertJsonValue(DatabaseColumn column, JsonNode? value)
    {
        if (value is null || value.ToJsonString() == "null")
        {
            return null;
        }

        return column.Type switch
        {
            DatabaseColumnType.Boolean => GetValue<bool>(value),
            DatabaseColumnType.Integer => GetValue<int>(value),
            DatabaseColumnType.Jsonb => value.ToJsonString(),
            DatabaseColumnType.Timestamp => ParseTimestamp(value),
            DatabaseColumnType.Uuid => ParseUuid(value),
            _ => ParseText(value)
        };
    }

    private static string ParseText(JsonNode value)
    {
        return value is JsonValue jsonValue && jsonValue.TryGetValue<string>(out var text)
            ? text
            : value.ToJsonString();
    }

    private static Guid ParseUuid(JsonNode value)
    {
        if (value is JsonValue jsonValue && jsonValue.TryGetValue<Guid>(out var guid))
        {
            return guid;
        }

        return Guid.Parse(ParseText(value));
    }

    private static DateTimeOffset ParseTimestamp(JsonNode value)
    {
        if (value is JsonValue jsonValue && jsonValue.TryGetValue<DateTimeOffset>(out var timestamp))
        {
            return timestamp;
        }

        return DateTimeOffset.Parse(ParseText(value), CultureInfo.InvariantCulture);
    }

    private static T GetValue<T>(JsonNode value)
    {
        if (value is JsonValue jsonValue && jsonValue.TryGetValue<T>(out var typedValue))
        {
            return typedValue;
        }

        return JsonSerializer.Deserialize<T>(value.ToJsonString())
            ?? throw new InvalidOperationException($"Could not read {typeof(T).Name} from JSON value.");
    }

    private string SelectColumns()
    {
        return string.Join(", ", table.Columns.Select(column => Quote(column.Name)));
    }

    private string QualifiedTableName()
    {
        return $"public.{Quote(table.TableName)}";
    }

    private static string Quote(string identifier)
    {
        return $"\"{identifier.Replace("\"", "\"\"", StringComparison.Ordinal)}\"";
    }
}
