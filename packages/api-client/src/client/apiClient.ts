export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface ApiClientOptions {
  getAccessToken?: () => string | null;
  onUnauthorized?: () => void;
}

export class ApiClient {
  constructor(
    private baseUrl: string,
    private options: ApiClientOptions = {},
  ) {}

  async request<T>(
    endpoint: string,
    method: HttpMethod = "GET",
    body?: unknown,
  ): Promise<T> {
    const token = this.options.getAccessToken?.();

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token && {
          Authorization: `Bearer ${token}`,
        }),
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      if (response.status === 401) {
        this.options.onUnauthorized?.();
      }

      throw new Error(data?.detail ?? data?.message ?? "Request failed");
    }

    return data;
  }

  get<T>(endpoint: string) {
    return this.request<T>(endpoint);
  }

  post<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, "POST", body);
  }

  put<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, "PUT", body);
  }

  patch<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, "PATCH", body);
  }

  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, "DELETE");
  }
}
