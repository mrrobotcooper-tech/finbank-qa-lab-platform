import { qaConfig } from "../framework/config";
import { expect, test } from "../framework/fixtures";
import { formatViolations, scanAxe } from "../framework/axe";

test("NFR-A11Y-001 login sin violaciones graves de axe @a11y @critical", async ({
  loginPage,
  page,
}, testInfo) => {
  await loginPage.goto();
  const scan = await scanAxe(page, "login", testInfo);
  expect(scan.blocking, formatViolations(scan.blocking)).toEqual([]);
});

test("NFR-A11Y-001 dashboard de cuentas sin violaciones graves de axe @a11y @critical @seed", async ({
  loginPage,
  accountsPage,
  page,
}, testInfo) => {
  await loginPage.goto();
  await loginPage.login(qaConfig.seed.ana.email, qaConfig.seed.ana.password);
  await accountsPage.waitForLoaded();
  const scan = await scanAxe(page, "accounts", testInfo);
  expect(scan.blocking, formatViolations(scan.blocking)).toEqual([]);
});

test("NFR-A11Y-001 transferencia sin violaciones graves de axe @a11y @critical @seed", async ({
  loginPage,
  transferPage,
  page,
}, testInfo) => {
  await loginPage.goto();
  await loginPage.login(qaConfig.seed.ana.email, qaConfig.seed.ana.password);
  await transferPage.goto();
  await expect(page.getByTestId("transfer-form")).toBeVisible();
  await expect(page.getByTestId("transfer-source")).not.toHaveValue("");
  const scan = await scanAxe(page, "transfer", testInfo);
  expect(scan.blocking, formatViolations(scan.blocking)).toEqual([]);
});

test("NFR-A11Y-001 admin sin violaciones graves de axe @a11y @critical @seed", async ({
  loginPage,
  adminPage,
  page,
}, testInfo) => {
  await loginPage.goto();
  await loginPage.login(qaConfig.seed.admin.email, qaConfig.seed.admin.password);
  await adminPage.goto();
  await expect(adminPage.heading()).toBeVisible();
  await expect(adminPage.usersTable().locator("tbody tr").first()).toBeVisible();
  const scan = await scanAxe(page, "admin", testInfo);
  expect(scan.blocking, formatViolations(scan.blocking)).toEqual([]);
});
