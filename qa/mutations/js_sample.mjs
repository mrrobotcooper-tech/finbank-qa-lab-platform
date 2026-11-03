import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "../..");
const target = join(root, "apps/frontend/src/lib/money.ts");
const original = readFileSync(target, "utf8");
const mutant = original.replace("if (!match)", "if (false)");
if (mutant === original) {
  console.error("No se aplicó el mutante JS; el ancla cambió.");
  process.exit(2);
}

writeFileSync(target, mutant);
let code = 1;
try {
  const result = spawnSync("npm", ["run", "test", "--", "src/lib/money.test.ts"], {
    cwd: join(root, "apps/frontend"),
    stdio: "inherit",
  });
  code = result.status ?? 1;
} finally {
  writeFileSync(target, original);
}

if (code === 0) {
  console.error("SOBREVIVIÓ: toCents mutado no fue detectado.");
  process.exit(1);
}
console.log(`KILLED: vitest exit ${code} con toCents mutado.`);
