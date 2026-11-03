import { useEffect, useState } from "react";

import { fetchReady, toSystemView, type SystemView } from "../api/ready";

type LoadState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ok"; view: SystemView };

export function StatusPage() {
  const [state, setState] = useState<LoadState>({ kind: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    fetchReady(controller.signal)
      .then((payload) => setState({ kind: "ok", view: toSystemView(payload) }))
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        const message = error instanceof Error ? error.message : "Error desconocido";
        setState({ kind: "error", message });
      });
    return () => controller.abort();
  }, []);

  return (
    <article>
      <h1>Estado del sistema</h1>
      <p>
        La SPA consulta <code>/ready</code> en la API. Liveness no implica que Postgres,
        Redis o RabbitMQ estén disponibles.
      </p>
      {state.kind === "loading" ? <p role="status">Consultando dependencias…</p> : null}
      {state.kind === "error" ? (
        <p role="alert" className="alert">
          {state.message}
        </p>
      ) : null}
      {state.kind === "ok" ? <StatusPanel view={state.view} /> : null}
    </article>
  );
}

function StatusPanel({ view }: { view: SystemView }) {
  return (
    <section aria-labelledby="resumen-estado">
      <h2 id="resumen-estado" data-testid="system-summary">
        {view.healthy ? "Todos los componentes responden" : "Hay componentes degradados"}
      </h2>
      <p className="meta">
        Correlation ID: <code data-testid="correlation-id">{view.correlationId}</code>
      </p>
      <table className="status-table">
        <caption className="visually-hidden">Dependencias de infraestructura</caption>
        <thead>
          <tr>
            <th scope="col">Componente</th>
            <th scope="col">Estado</th>
          </tr>
        </thead>
        <tbody>
          {view.components.map((component) => (
            <tr key={component.name} data-testid={`component-${component.name}`}>
              <th scope="row">{component.name}</th>
              <td>
                <span className={component.status === "up" ? "pill pill--up" : "pill pill--down"}>
                  {component.status}
                </span>
                {component.detail ? <span className="detail"> {component.detail}</span> : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
