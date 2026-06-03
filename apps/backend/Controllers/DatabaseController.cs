namespace ProIn.Backend.Controllers;

using Microsoft.AspNetCore.Mvc;
using Npgsql;

[Route("api/database")]
public sealed class DatabaseController(
    IConfiguration configuration,
    ILogger<DatabaseController> logger) : ApiControllerBase
{
    [HttpGet("health", Name = "GetDatabaseHealth")]
    public async Task<ActionResult<DatabaseHealthResponse>> GetHealth(CancellationToken cancellationToken)
    {
        var connectionString =
            configuration.GetConnectionString("DefaultConnection")
            ?? configuration["DATABASE_URL"];

        if (string.IsNullOrWhiteSpace(connectionString))
        {
            return Ok(new DatabaseHealthResponse(
                "not_configured",
                DateTimeOffset.UtcNow,
                "Set ConnectionStrings:DefaultConnection or DATABASE_URL for the Supabase Postgres connection."));
        }

        try
        {
            await using var connection = new NpgsqlConnection(connectionString);
            await connection.OpenAsync(cancellationToken);

            await using var command = new NpgsqlCommand(
                "select current_database(), current_schema()",
                connection);
            await using var reader = await command.ExecuteReaderAsync(cancellationToken);
            await reader.ReadAsync(cancellationToken);

            return Ok(new DatabaseHealthResponse(
                "healthy",
                DateTimeOffset.UtcNow,
                $"{reader.GetString(0)}.{reader.GetString(1)}"));
        }
        catch (Exception ex)
        {
            logger.LogWarning(ex, "Supabase database health check failed.");

            return StatusCode(
                StatusCodes.Status503ServiceUnavailable,
                new DatabaseHealthResponse(
                    "unhealthy",
                    DateTimeOffset.UtcNow,
                    "Could not connect to Supabase Postgres."));
        }
    }
}
