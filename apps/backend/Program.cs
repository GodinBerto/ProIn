using ProIn.Backend;

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

public sealed record WorkerHeartbeatRequest(string WorkerName);

public sealed record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
