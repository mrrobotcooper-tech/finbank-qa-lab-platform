import { describe, expect, it } from "vitest";

import { toSystemView, type ReadyResponse } from "./ready";

describe("toSystemView", () => {
  it("marca el sistema saludable solo si todos los componentes están up", () => {
    const payload: ReadyResponse = {
      status: "ok",
      correlation_id: "abc",
      components: [
        { name: "postgres", status: "up" },
        { name: "redis", status: "up" },
        { name: "rabbitmq", status: "up" },
      ],
    };
    expect(toSystemView(payload)).toEqual({
      healthy: true,
      correlationId: "abc",
      components: payload.components,
    });
  });

  it("marca degradado si el API reporta ok pero un componente está down", () => {
    const payload: ReadyResponse = {
      status: "ok",
      correlation_id: "abc",
      components: [
        { name: "postgres", status: "up" },
        { name: "redis", status: "down" },
      ],
    };
    expect(toSystemView(payload).healthy).toBe(false);
  });

  it("marca degradado cuando el API responde degraded", () => {
    const payload: ReadyResponse = {
      status: "degraded",
      correlation_id: "xyz",
      components: [{ name: "rabbitmq", status: "down", detail: "timeout" }],
    };
    expect(toSystemView(payload).healthy).toBe(false);
  });
});
