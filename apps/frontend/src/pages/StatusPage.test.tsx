import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { StatusPage } from "./StatusPage";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("StatusPage", () => {
  it("renderiza componentes cuando /ready responde 200", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          status: "ok",
          correlation_id: "cid-1",
          components: [
            { name: "postgres", status: "up" },
            { name: "redis", status: "up" },
            { name: "rabbitmq", status: "up" },
          ],
        }),
      }),
    );

    render(<StatusPage />);
    expect(await screen.findByTestId("system-summary")).toHaveTextContent(
      "Todos los componentes responden",
    );
    expect(screen.getByTestId("component-postgres")).toHaveTextContent("up");
    expect(screen.getByTestId("correlation-id")).toHaveTextContent("cid-1");
  });

  it("muestra degradación cuando /ready responde 503", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({
          status: "degraded",
          correlation_id: "cid-2",
          components: [{ name: "redis", status: "down", detail: "connection refused" }],
        }),
      }),
    );

    render(<StatusPage />);
    expect(await screen.findByTestId("system-summary")).toHaveTextContent("degradados");
    expect(screen.getByTestId("component-redis")).toHaveTextContent("down");
  });

  it("anuncia error cuando /ready no es alcanzable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network down")));
    render(<StatusPage />);
    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Network down");
    });
  });
});
