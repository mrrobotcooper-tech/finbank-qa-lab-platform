import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

import AxeBuilder from "@axe-core/playwright";
import type { Page, TestInfo } from "@playwright/test";
import type { AxeResults, Result } from "axe-core";

const BLOCKING_IMPACT = new Set(["critical", "serious"]);

export type AxeScanResult = {
  results: AxeResults;
  blocking: Result[];
  reportPath: string;
};

export async function scanAxe(page: Page, name: string, testInfo?: TestInfo): Promise<AxeScanResult> {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  const dir = path.resolve("reports/axe");
  await mkdir(dir, { recursive: true });
  const reportPath = path.join(dir, `${name}.json`);
  await writeFile(reportPath, JSON.stringify(results, null, 2));
  if (testInfo) {
    await testInfo.attach(`axe-${name}`, {
      path: reportPath,
      contentType: "application/json",
    });
  }
  const blocking = results.violations.filter((item) => BLOCKING_IMPACT.has(item.impact ?? ""));
  return { results, blocking, reportPath };
}

export function formatViolations(violations: Result[]): string {
  return violations
    .map((item) => {
      const nodes = item.nodes.map((node) => `    - ${node.target.join(" ")}`).join("\n");
      return `${item.id} [${item.impact}] ${item.help}\n${nodes}`;
    })
    .join("\n");
}
