import { readFileSync } from "node:fs";

const reportPath = process.argv[2] ?? "reports/zap/zap-baseline.json";

function asSites(payload) {
  const site = payload.site;
  if (!site) {
    return [];
  }
  return Array.isArray(site) ? site : [site];
}

const payload = JSON.parse(readFileSync(reportPath, "utf8"));
const alerts = asSites(payload).flatMap((site) => site.alerts ?? []);
const high = alerts.filter((alert) => Number.parseInt(String(alert.riskcode), 10) >= 3);

const summary = alerts.map(
  (alert) =>
    `${alert.riskdesc ?? alert.riskcode} · ${alert.name ?? alert.alert} (plugin ${alert.pluginid})`,
);
console.log(`ZAP baseline: ${alerts.length} alertas en ${reportPath}`);
for (const line of summary) {
  console.log(`  - ${line}`);
}

if (high.length > 0) {
  console.error(`Hay ${high.length} alerta(s) High/Critical. El gate de Fase 7 falla.`);
  process.exit(1);
}

console.log("Gate OK: cero alertas High/Critical.");
