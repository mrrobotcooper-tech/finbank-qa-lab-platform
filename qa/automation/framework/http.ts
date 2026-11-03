import type { APIRequestContext, APIResponse } from "@playwright/test";

import { qaConfig } from "./config";

export type RequestOptions = {
  data?: unknown;
  token?: string;
  idempotencyKey?: string;
  correlationId?: string;
  headers?: Record<string, string>;
};

export class HttpClient {
  constructor(
    private readonly request: APIRequestContext,
    private readonly baseURL: string = qaConfig.apiUrl,
  ) {}

  get(path: string, options: RequestOptions = {}): Promise<APIResponse> {
    return this.send("GET", path, options);
  }

  post(path: string, options: RequestOptions = {}): Promise<APIResponse> {
    return this.send("POST", path, options);
  }

  patch(path: string, options: RequestOptions = {}): Promise<APIResponse> {
    return this.send("PATCH", path, options);
  }

  private send(
    method: "GET" | "POST" | "PATCH",
    path: string,
    options: RequestOptions,
  ): Promise<APIResponse> {
    const headers: Record<string, string> = {
      Accept: "application/json",
      [qaConfig.correlationHeader]: options.correlationId ?? crypto.randomUUID(),
      ...options.headers,
    };
    if (options.token) {
      headers.Authorization = `Bearer ${options.token}`;
    }
    if (options.idempotencyKey) {
      headers["Idempotency-Key"] = options.idempotencyKey;
    }
    return this.request.fetch(`${this.baseURL}${path}`, {
      method,
      headers,
      data: options.data,
    });
  }
}
