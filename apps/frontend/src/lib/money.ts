export function toCents(input: string): number {
  const normalized = input.trim().replace(",", ".");
  const match = /^(\d+)(?:\.(\d{1,2}))?$/.exec(normalized);
  if (!match) {
    throw new Error("Importe inválido");
  }
  const whole = Number(match[1]);
  const fraction = Number((match[2] ?? "00").padEnd(2, "0"));
  return whole * 100 + fraction;
}

export function formatMoney(cents: number, currency: string): string {
  const sign = cents < 0 ? "-" : "";
  const absolute = Math.abs(cents);
  const whole = Math.floor(absolute / 100);
  const fraction = String(absolute % 100).padStart(2, "0");
  return `${sign}${currency} ${whole.toLocaleString("es-AR")},${fraction}`;
}
