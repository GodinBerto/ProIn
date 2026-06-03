namespace ProIn.Workers;

using System.Net.Http.Json;
using Microsoft.Extensions.Options;

public sealed class Worker(
    ILogger<Worker> logger,
    IHttpClientFactory httpClientFactory,
    IOptions<WorkerOptions> options) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var workerOptions = options.Value;
        var client = httpClientFactory.CreateClient(nameof(Worker));
        client.BaseAddress = new Uri(workerOptions.BackendBaseUrl.TrimEnd('/') + "/");
        client.Timeout = TimeSpan.FromSeconds(10);

        logger.LogInformation(
            "Worker {WorkerName} started. Heartbeats will be sent to {BackendBaseUrl}.",
            workerOptions.Name,
            workerOptions.BackendBaseUrl);

        while (!stoppingToken.IsCancellationRequested)
        {
            await SendHeartbeatAsync(client, workerOptions, stoppingToken);

            await Task.Delay(
                TimeSpan.FromSeconds(workerOptions.HeartbeatIntervalSeconds),
                stoppingToken);
        }
    }

    private async Task SendHeartbeatAsync(
        HttpClient client,
        WorkerOptions workerOptions,
        CancellationToken stoppingToken)
    {
        try
        {
            var backendHealth = await client.GetFromJsonAsync<BackendHealthResponse>(
                "api/health",
                stoppingToken);

            using var heartbeatPayload = JsonContent.Create(new WorkerHeartbeatRequest(workerOptions.Name));
            using var response = await client.PostAsync(
                "api/workers/heartbeat",
                heartbeatPayload,
                stoppingToken);

            response.EnsureSuccessStatusCode();

            logger.LogInformation(
                "Heartbeat acknowledged by backend at {Time}. Backend status: {Status}.",
                DateTimeOffset.UtcNow,
                backendHealth?.Status ?? "unknown");
        }
        catch (Exception ex)
        {
            logger.LogWarning(
                ex,
                "Heartbeat failed for backend {BackendBaseUrl}.",
                workerOptions.BackendBaseUrl);
        }
    }
}

public sealed class WorkerOptions
{
    public string Name { get; set; } = "queue-worker";

    public string BackendBaseUrl { get; set; } = "http://localhost:5236";

    public int HeartbeatIntervalSeconds { get; set; } = 15;
}

public sealed record BackendHealthResponse(string Status, DateTimeOffset TimestampUtc);

public sealed record WorkerHeartbeatRequest(string WorkerName);
