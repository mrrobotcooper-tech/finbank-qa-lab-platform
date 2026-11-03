import { paymentSchema, type Payment } from "../schemas";
import type { HttpClient } from "../http";

export type PaymentCreateInput = {
  account_id: string;
  amount: number;
  currency: string;
  payment_type: string;
  payee: string;
  scheduled_at?: string;
};

export class PaymentsClient {
  constructor(private readonly http: HttpClient) {}

  async create(token: string, input: PaymentCreateInput, idempotencyKey?: string): Promise<Payment> {
    const response = await this.createRaw(token, input, idempotencyKey);
    if (response.status() !== 201) {
      throw new Error(`Payment failed: ${response.status()} ${await response.text()}`);
    }
    return paymentSchema.parse(await response.json());
  }

  createRaw(token: string | undefined, input: PaymentCreateInput, idempotencyKey?: string) {
    return this.http.post("/api/v1/payments", {
      token,
      data: input,
      idempotencyKey: idempotencyKey ?? crypto.randomUUID(),
    });
  }

  async list(token: string): Promise<Payment[]> {
    const response = await this.http.get("/api/v1/payments", { token });
    if (response.status() !== 200) {
      throw new Error(`Payments failed: ${response.status()} ${await response.text()}`);
    }
    return paymentSchema.array().parse(await response.json());
  }

  async get(token: string, paymentId: string): Promise<Payment> {
    const response = await this.http.get(`/api/v1/payments/${paymentId}`, { token });
    if (response.status() !== 200) {
      throw new Error(`Payment get failed: ${response.status()} ${await response.text()}`);
    }
    return paymentSchema.parse(await response.json());
  }
}
