export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(status: number, detail: string, code?: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

type JsonBody = Record<string, unknown> | undefined;

type RequestOptions = {
  method?: string;
  token?: string | null;
  body?: JsonBody;
  headers?: Record<string, string>;
  signal?: AbortSignal;
};

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }
  const init: RequestInit = {
    method: options.method ?? "GET",
    credentials: "include",
    headers,
    signal: options.signal,
  };
  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
    init.body = JSON.stringify(options.body);
  }
  const response = await fetch(path, init);
  const payload = (await response.json().catch(() => ({}))) as {
    detail?: string;
    code?: string;
  };
  if (!response.ok) {
    const detail =
      typeof payload.detail === "string" ? payload.detail : `Error HTTP ${response.status}`;
    throw new ApiError(response.status, detail, payload.code);
  }
  return payload as T;
}

export function newIdempotencyKey(): string {
  try {
    if (typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
  } catch {
    /* http://web in Compose is not a secure context */
  }
  return `idemp-${Date.now()}-${Math.random().toString(16).slice(2)}${Math.random().toString(16).slice(2)}`;
}
