using ProIn.Backend;
using Npgsql;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
builder.Services.AddCors(options =>
{
    options.AddPolicy("Frontend", policy =>
    {
        var frontendOrigin = builder.Configuration["Frontend:Origin"] ?? "http://localhost:3000";

        policy.WithOrigins(frontendOrigin)
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});
builder.Services.AddSingleton<WorkerStatusStore>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseCors("Frontend");

app.MapGet("/api/health", () =>
    Results.Ok(new ApiHealthResponse("healthy", DateTimeOffset.UtcNow)))
    .WithName("GetHealth");

app.MapGet("/api/workers/status", (WorkerStatusStore store) =>
    Results.Ok(store.GetSnapshot()))
    .WithName("GetWorkerStatus");

app.MapGet("/api/database/health", async (
    IConfiguration configuration,
    ILoggerFactory loggerFactory,
    CancellationToken cancellationToken) =>
{
    var connectionString =
        configuration.GetConnectionString("DefaultConnection")
        ?? configuration["DATABASE_URL"];

    if (string.IsNullOrWhiteSpace(connectionString))
    {
        return Results.Ok(new DatabaseHealthResponse(
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

        return Results.Ok(new DatabaseHealthResponse(
            "healthy",
            DateTimeOffset.UtcNow,
            $"{reader.GetString(0)}.{reader.GetString(1)}"));
    }
    catch (Exception ex)
    {
        var logger = loggerFactory.CreateLogger("DatabaseHealth");
        logger.LogWarning(ex, "Supabase database health check failed.");

        return Results.Json(
            new DatabaseHealthResponse(
                "unhealthy",
                DateTimeOffset.UtcNow,
                "Could not connect to Supabase Postgres."),
            statusCode: StatusCodes.Status503ServiceUnavailable);
    }
})
.WithName("GetDatabaseHealth");

app.MapPost("/api/workers/heartbeat", (WorkerHeartbeatRequest request, WorkerStatusStore store) =>
{
    if (string.IsNullOrWhiteSpace(request.WorkerName))
    {
        return Results.BadRequest(new { message = "workerName is required." });
    }

    store.RecordHeartbeat(request.WorkerName);
    return Results.Accepted();
})
.WithName("RecordWorkerHeartbeat");

var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

app.MapGet("/api/weatherforecast", () =>
{
    var forecast = Enumerable.Range(1, 5).Select(index =>
        new WeatherForecast(
            DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
            Random.Shared.Next(-20, 55),
            summaries[Random.Shared.Next(summaries.Length)]))
        .ToArray();

    return forecast;
})
.WithName("GetWeatherForecast");

app.Run();

public sealed record ApiHealthResponse(string Status, DateTimeOffset TimestampUtc);

public sealed record DatabaseHealthResponse(
    string Status,
    DateTimeOffset TimestampUtc,
    string Detail);

public sealed record WorkerHeartbeatRequest(string WorkerName);

public sealed record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
