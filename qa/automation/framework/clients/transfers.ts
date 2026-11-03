import { transferSchema, type Transfer } from "../schemas";
import type { HttpClient } from "../http";

export type TransferCreateInput = {
  source_account_id: string;
  destination_account_id?: string;
  destination_account_number?: string;
  amount: number;
  currency: string;
};

export class TransfersClient {
  constructor(private readonly http: HttpClient) {}

  async create(token: string, input: TransferCreateInput, idempotencyKey?: string): Promise<Transfer> {
    const response = await this.createRaw(token, input, idempotencyKey);
    if (response.status() !== 201) {
      throw new Error(`Transfer failed: ${response.status()} ${await response.text()}`);
    }
    return transferSchema.parse(await response.json());
  }

  createRaw(token: string | undefined, input: TransferCreateInput, idempotencyKey?: string) {
    return this.http.post("/api/v1/transfers", {
      token,
      data: input,
      idempotencyKey: idempotencyKey ?? crypto.randomUUID(),
    });
  }

  async list(token: string): Promise<Transfer[]> {
    const response = await this.http.get("/api/v1/transfers", { token });
    if (response.status() !== 200) {
      throw new Error(`Transfers failed: ${response.status()} ${await response.text()}`);
    }
    return transferSchema.array().parse(await response.json());
  }

  async get(token: string, transferId: string): Promise<Transfer> {
    const response = await this.http.get(`/api/v1/transfers/${transferId}`, { token });
    if (response.status() !== 200) {
      throw new Error(`Transfer get failed: ${response.status()} ${await response.text()}`);
    }
    return transferSchema.parse(await response.json());
  }

  getRaw(token: string | undefined, transferId: string) {
    return this.http.get(`/api/v1/transfers/${transferId}`, { token });
  }
}
