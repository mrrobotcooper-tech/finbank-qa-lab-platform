export function uniqueCents(min = 121, max = 980): number {
  const span = max - min + 1;
  const entropy = Number.parseInt(crypto.randomUUID().replaceAll("-", "").slice(0, 8), 16);
  return min + (entropy % span);
}

export function fromCents(cents: number): string {
  const whole = Math.trunc(cents / 100);
  const fraction = String(Math.abs(cents % 100)).padStart(2, "0");
  return `${whole}.${fraction}`;
}

export function toCents(input: string): number {
  const normalized = input.trim().replace(",", ".");
  const match = /^(\d+)(?:\.(\d{1,2}))?$/.exec(normalized);
  if (!match) {
    throw new Error(`Importe inválido: ${input}`);
  }
  const whole = Number(match[1]);
  const fraction = Number((match[2] ?? "00").padEnd(2, "0"));
  return whole * 100 + fraction;
}

export function assertIntegerCents(value: number): void {
  if (!Number.isInteger(value)) {
    throw new Error(`El dinero debe ser entero en centavos, recibido ${value}`);
  }
}
