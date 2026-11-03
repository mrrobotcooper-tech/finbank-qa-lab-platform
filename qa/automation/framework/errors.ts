import type { APIResponse } from "@playwright/test";

import { errorSchema } from "./schemas";

export async function parseError(response: APIResponse): Promise<{ detail: string; code?: string }> {
  const body = errorSchema.parse(await response.json());
  const detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
  return { detail, code: body.code };
}
