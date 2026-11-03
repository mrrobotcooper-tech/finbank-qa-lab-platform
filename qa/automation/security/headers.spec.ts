import { expect, test } from "../framework/fixtures";

const REQUIRED_API_HEADERS = {
  "x-content-type-options": "nosniff",
  "x-frame-options": "DENY",
  "referrer-policy": "no-referrer",
};

test("NFR-SEC-007 la API publica headers de seguridad @security @critical", async ({ api }) => {
  const response = await api.http.get("/health");
  expect(response.status()).toBe(200);
  const headers = response.headers();
  for (const [name, value] of Object.entries(REQUIRED_API_HEADERS)) {
    expect(headers[name], name).toBe(value);
  }
  expect(headers["content-security-policy"]).toContain("frame-ancestors 'none'");
  expect(headers["permissions-policy"]).toContain("camera=()");
});

test("NFR-SEC-007 el frontend servido publica headers de seguridad @security @critical", async ({
  page,
}) => {
  const response = await page.goto("/");
  expect(response).toBeTruthy();
  const headers = response!.headers();
  expect(headers["x-content-type-options"]).toBe("nosniff");
  expect(headers["x-frame-options"]).toBe("DENY");
  expect(headers["content-security-policy"]).toContain("default-src 'self'");
  expect(headers["content-security-policy"]).toContain("frame-ancestors 'none'");
});

test("NFR-SEC-005 la cookie de refresh es HttpOnly y SameSite=Lax @security @critical @seed", async ({
  api,
}) => {
  const response = await api.auth.loginRaw("ana@finbank.test", "Customer1!");
  expect(response.status()).toBe(200);
  const setCookie = response
    .headersArray()
    .filter((header) => header.name.toLowerCase() === "set-cookie")
    .map((header) => header.value)
    .join("\n");
  expect(setCookie).toMatch(/finbank_refresh=/);
  expect(setCookie).toMatch(/HttpOnly/i);
  expect(setCookie).toMatch(/SameSite=Lax/i);
});
