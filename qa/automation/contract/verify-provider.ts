import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { z } from "zod";

const healthSchema = z.object({
  status: z.string().min(1),
  service: z.string().min(1),
  environment: z.string().min(1),
  correlation_id: z.string(),
});

type PactFile = {
  consumer: { name: string };
  provider: { name: string };
  interactions: Array<{
    description: string;
    request: { method: string; path: string };
    response: { status: number; body: unknown };
  }>;
};

const root = dirname(fileURLToPath(import.meta.url));
const pactPath = join(root, "pacts/finbank-qa-finbank-api.json");
const apiUrl = process.env.FINBANK_API_URL ?? process.env.QA_API_URL ?? "http://127.0.0.1:8000";

const pact = JSON.parse(readFileSync(pactPath, "utf8")) as PactFile;
const interaction = pact.interactions[0];
if (!interaction) {
  throw new Error("Pact sin interacciones");
}

const response = await fetch(`${apiUrl}${interaction.request.path}`, {
  method: interaction.request.method,
});
if (response.status !== interaction.response.status) {
  throw new Error(`Provider ${response.status}, pact esperaba ${interaction.response.status}`);
}

const body: unknown = await response.json();
const parsed = healthSchema.parse(body);
const expected = healthSchema.parse(interaction.response.body);

if (parsed.status !== expected.status) {
  throw new Error(`status '${parsed.status}' ≠ contrato '${expected.status}'`);
}
if (parsed.service !== expected.service) {
  throw new Error(`service '${parsed.service}' ≠ contrato '${expected.service}'`);
}

console.log(
  `Pact OK: ${pact.consumer.name} → ${pact.provider.name} ${interaction.request.method} ${interaction.request.path}`,
);
console.log(`  status=${parsed.status} service=${parsed.service} env=${parsed.environment}`);
