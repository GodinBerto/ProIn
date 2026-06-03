namespace ProIn.Backend;

public sealed record ApiHealthResponse(string Status, DateTimeOffset TimestampUtc);

public sealed record DatabaseHealthResponse(
    string Status,
    DateTimeOffset TimestampUtc,
    string Detail);

public sealed record WorkerHeartbeatRequest(string WorkerName);
