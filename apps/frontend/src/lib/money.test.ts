import { describe, expect, it } from "vitest";

import { formatMoney, toCents } from "./money";

describe("money", () => {
  it("convierte importes decimales a centavos sin float", () => {
    expect(toCents("150")).toBe(15000);
    expect(toCents("150,5")).toBe(15050);
    expect(toCents("150.05")).toBe(15005);
  });

  it("rechaza importes inválidos", () => {
    expect(() => toCents("abc")).toThrow("Importe inválido");
  });

  it("formatea centavos para pantalla", () => {
    expect(formatMoney(100, "USD")).toBe("USD 1,00");
    expect(formatMoney(50, "ARS")).toBe("ARS 0,50");
  });
});
