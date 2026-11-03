import { expect, test } from "../framework/fixtures";

test("NFR-A11Y-003 skip link y foco visible en login @a11y @critical", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("login-form").waitFor();
  await page.keyboard.press("Tab");
  const skip = page.getByTestId("skip-link");
  await expect(skip).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#contenido")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByTestId("login-email")).toBeFocused();
  const outline = await page.getByTestId("login-email").evaluate((element) => {
    const style = getComputedStyle(element);
    return { width: style.outlineWidth, style: style.outlineStyle };
  });
  expect(Number.parseInt(outline.width, 10)).toBeGreaterThan(0);
  expect(outline.style).not.toBe("none");
});

test("NFR-A11Y-002 el formulario de login se recorre con teclado @a11y @critical", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("login-email").focus();
  await page.keyboard.press("Tab");
  await expect(page.getByTestId("login-password")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByTestId("login-submit")).toBeFocused();
});
