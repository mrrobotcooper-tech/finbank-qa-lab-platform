import { expect, test } from "../framework/fixtures";
import { healthSchema, readySchema } from "../framework/schemas";

test("API liveness responde ok @smoke @critical", async ({ api }) => {
  const response = await api.http.get("/health");
  expect(response.status()).toBe(200);
  const body = healthSchema.parse(await response.json());
  expect(body.status).toBe("ok");
});

test("API readiness exige postgres redis y rabbitmq @smoke @critical", async ({ api }) => {
  const response = await api.http.get("/ready");
  expect(response.status(), await response.text()).toBe(200);
  const body = readySchema.parse(await response.json());
  expect(body.status).toBe("ok");
  const names = body.components.map((item) => item.name).sort();
  expect(names).toEqual(["postgres", "rabbitmq", "redis"]);
  expect(body.components.every((item) => item.status === "up")).toBe(true);
});

test("el historial completo de auditoría no se expone por API @smoke @critical", async ({ api }) => {
  const response = await api.http.get("/api/v1/admin/audit");
  expect(response.status()).toBe(404);
});
