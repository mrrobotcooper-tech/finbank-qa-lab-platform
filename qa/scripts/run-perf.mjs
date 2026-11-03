import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const qaRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const outDir = join(qaRoot, "reports/perf");
mkdirSync(outDir, { recursive: true });

const scenarios = ["login", "accounts", "transfers"];

function latency(report) {
  const agg = report.aggregate ?? {};
  const summary = agg.summaries?.["http.response_time"] ?? agg.summaries?.httpResponseTime;
  if (summary) {
    return {
      min: summary.min,
      p50: summary.p50,
      p95: summary.p95,
      p99: summary.p99,
      max: summary.max,
    };
  }
  if (agg.latency) {
    return {
      min: agg.latency.min,
      p50: agg.latency.p50,
      p95: agg.latency.p95,
      p99: agg.latency.p99,
      max: agg.latency.max,
    };
  }
  return { min: null, p50: null, p95: null, p99: null, max: null };
}

function rates(report) {
  const agg = report.aggregate ?? {};
  const counters = agg.counters ?? {};
  const codes = Object.entries(counters)
    .filter(([key]) => key.startsWith("http.codes."))
    .map(([key, value]) => [key.replace("http.codes.", ""), Number(value)]);
  const ok = codes
    .filter(([code]) => String(code).startsWith("2"))
    .reduce((sum, [, n]) => sum + n, 0);
  const total =
    Number(counters["http.requests"] ?? counters["http.downloaded"] ?? 0) ||
    codes.reduce((sum, [, n]) => sum + n, 0);
  const errors = Number(counters["errors.ETIMEDOUT"] ?? 0) + Number(agg.errors ? Object.values(agg.errors).reduce((a, b) => a + Number(b), 0) : 0);
  const failed = total > 0 ? Math.max(total - ok, 0) : errors;
  const errorRate = total > 0 ? failed / total : errors > 0 ? 1 : 0;
  return { total, ok, failed, errorRate, counters };
}

const rows = [];
for (const name of scenarios) {
  const jsonPath = join(outDir, `${name}.json`);
  const result = spawnSync(
    "npx",
    ["artillery", "run", "--output", jsonPath, `automation/performance/${name}.yml`],
    { cwd: qaRoot, stdio: "inherit", env: process.env },
  );
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
  const report = JSON.parse(readFileSync(jsonPath, "utf8"));
  const lat = latency(report);
  const traffic = rates(report);
  rows.push({ name, ...lat, ...traffic });
  console.log(
    `${name}: p50=${lat.p50} p95=${lat.p95} requests=${traffic.total} errorRate=${(traffic.errorRate * 100).toFixed(2)}%`,
  );
}

writeFileSync(join(outDir, "summary.json"), JSON.stringify({ generatedAt: new Date().toISOString(), rows }, null, 2));
console.log(`Resumen: ${join(outDir, "summary.json")}`);
