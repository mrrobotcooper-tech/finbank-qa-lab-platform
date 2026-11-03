export type ComponentState = "up" | "down";

export type ComponentStatus = {
  name: string;
  status: ComponentState;
  detail?: string;
};

export type ReadyResponse = {
  status: "ok" | "degraded";
  correlation_id: string;
  components: ComponentStatus[];
};

export type SystemView = {
  healthy: boolean;
  correlationId: string;
  components: ComponentStatus[];
};

export function toSystemView(payload: ReadyResponse): SystemView {
  return {
    healthy: payload.status === "ok" && payload.components.every((item) => item.status === "up"),
    correlationId: payload.correlation_id,
    components: payload.components,
  };
}

export async function fetchReady(signal?: AbortSignal): Promise<ReadyResponse> {
  const response = await fetch("/ready", {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok && response.status !== 503) {
    throw new Error(`No se pudo consultar /ready (HTTP ${response.status})`);
  }
  return (await response.json()) as ReadyResponse;
}
