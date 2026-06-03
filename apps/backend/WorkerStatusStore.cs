namespace ProIn.Backend;

using System.Collections.Concurrent;

public sealed class WorkerStatusStore
{
    private readonly ConcurrentDictionary<string, WorkerHeartbeatState> _workers =
        new(StringComparer.OrdinalIgnoreCase);

    public void RecordHeartbeat(string workerName)
    {
        var normalizedWorkerName = NormalizeWorkerName(workerName);

        _workers.AddOrUpdate(
            normalizedWorkerName,
            _ => WorkerHeartbeatState.Create(normalizedWorkerName),
            (_, existing) =>
            {
                existing.Touch();
                return existing;
            });
    }

    public WorkerStatusResponse GetSnapshot()
    {
        var generatedAtUtc = DateTimeOffset.UtcNow;
        var workers = _workers.Values
            .OrderBy(worker => worker.WorkerName, StringComparer.OrdinalIgnoreCase)
            .Select(worker => new WorkerStatusItem(
                worker.WorkerName,
                worker.LastSeenUtc,
                worker.HeartbeatCount,
                generatedAtUtc - worker.LastSeenUtc <= TimeSpan.FromSeconds(45)))
            .ToArray();

        return new WorkerStatusResponse(generatedAtUtc, workers);
    }

    private static string NormalizeWorkerName(string workerName)
    {
        var trimmedName = workerName.Trim();

        return string.IsNullOrWhiteSpace(trimmedName)
            ? "unnamed-worker"
            : trimmedName;
    }

    private sealed class WorkerHeartbeatState
    {
        private readonly object _gate = new();

        public string WorkerName { get; }

        public DateTimeOffset LastSeenUtc { get; private set; }

        public int HeartbeatCount { get; private set; }

        private WorkerHeartbeatState(string workerName)
        {
            WorkerName = workerName;
            LastSeenUtc = DateTimeOffset.UtcNow;
            HeartbeatCount = 1;
        }

        public static WorkerHeartbeatState Create(string workerName) => new(workerName);

        public void Touch()
        {
            lock (_gate)
            {
                LastSeenUtc = DateTimeOffset.UtcNow;
                HeartbeatCount++;
            }
        }
    }
}

public sealed record WorkerStatusResponse(
    DateTimeOffset GeneratedAtUtc,
    IReadOnlyList<WorkerStatusItem> Workers);

public sealed record WorkerStatusItem(
    string WorkerName,
    DateTimeOffset LastSeenUtc,
    int HeartbeatCount,
    bool IsHealthy);
