import styles from "./page.module.css";

type HealthResponse = {
  status: string;
  timestampUtc: string;
};

type WorkerStatusItem = {
  workerName: string;
  lastSeenUtc: string;
  heartbeatCount: number;
  isHealthy: boolean;
};

type WorkerStatusResponse = {
  generatedAtUtc: string;
  workers: WorkerStatusItem[];
};

type BackendSnapshot = {
  apiBaseUrl: string;
  health: HealthResponse | null;
  workerStatus: WorkerStatusResponse | null;
  error: string | null;
};

const backendBaseUrl =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:5236";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${backendBaseUrl}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function loadBackendSnapshot(): Promise<BackendSnapshot> {
  try {
    const [health, workerStatus] = await Promise.all([
      fetchJson<HealthResponse>("/api/health"),
      fetchJson<WorkerStatusResponse>("/api/workers/status"),
    ]);

    return {
      apiBaseUrl: backendBaseUrl,
      health,
      workerStatus,
      error: null,
    };
  } catch (error) {
    return {
      apiBaseUrl: backendBaseUrl,
      health: null,
      workerStatus: null,
      error:
        error instanceof Error
          ? error.message
          : "Backend is not reachable right now.",
    };
  }
}

function formatTimestamp(timestampUtc: string) {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(timestampUtc));
}

export default async function Home() {
  const snapshot = await loadBackendSnapshot();
  const activeWorkers =
    snapshot.workerStatus?.workers.filter((worker) => worker.isHealthy) ?? [];

  return (
    <main className={styles.page}>
      <section className={styles.shell}>
        <div className={styles.hero}>
          <p className={styles.kicker}>ProIn control plane</p>
          <h1>Backend, workers, and frontend are now wired together.</h1>
          <p className={styles.lede}>
            The frontend reads live API status from{" "}
            <code>{snapshot.apiBaseUrl}</code>, the backend tracks worker
            heartbeats, and the worker service reports in on a schedule.
          </p>
        </div>

        <div className={styles.grid}>
          <article className={styles.card}>
            <span className={styles.label}>Backend</span>
            <strong className={styles.value}>
              {snapshot.health ? snapshot.health.status : "offline"}
            </strong>
            <p className={styles.meta}>
              {snapshot.health
                ? `Last checked ${formatTimestamp(snapshot.health.timestampUtc)} UTC`
                : snapshot.error}
            </p>
          </article>

          <article className={styles.card}>
            <span className={styles.label}>Workers</span>
            <strong className={styles.value}>
              {snapshot.workerStatus?.workers.length ?? 0} registered
            </strong>
            <p className={styles.meta}>
              {activeWorkers.length} currently healthy
            </p>
          </article>

          <article className={`${styles.card} ${styles.spanTwo}`}>
            <span className={styles.label}>Heartbeat feed</span>
            {snapshot.workerStatus ? (
              <ul className={styles.list}>
                {snapshot.workerStatus.workers.map((worker) => (
                  <li key={worker.workerName} className={styles.listItem}>
                    <div>
                      <strong>{worker.workerName}</strong>
                      <span>
                        {worker.heartbeatCount} heartbeats, last seen{" "}
                        {formatTimestamp(worker.lastSeenUtc)} UTC
                      </span>
                    </div>
                    <span
                      className={`${styles.statusPill} ${
                        worker.isHealthy
                          ? styles.statusHealthy
                          : styles.statusStale
                      }`}
                    >
                      {worker.isHealthy ? "healthy" : "stale"}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={styles.meta}>
                Start the backend and workers to see live heartbeats here.
              </p>
            )}
          </article>
        </div>
      </section>
    </main>
  );
}
