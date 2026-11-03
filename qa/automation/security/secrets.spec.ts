import { expect, test } from "../framework/fixtures";

test("NFR-SEC-002 /health no filtra secretos @security @critical", async ({ api }) => {
  const response = await api.http.get("/health");
  const body = JSON.stringify(await response.json()).toLowerCase();
  expect(body).not.toMatch(/password|secret|postgres:\/\/|redis:\/\//);
});

test("NFR-SEC-007 CORS no refleja un Origin ajeno @security @critical", async ({ request }) => {
  const apiUrl = process.env.QA_API_URL ?? "http://localhost:8000";
  const response = await request.fetch(`${apiUrl}/health`, {
    headers: { Origin: "http://evil.example" },
  });
  expect(response.headers()["access-control-allow-origin"] ?? "").not.toBe("http://evil.example");
});
