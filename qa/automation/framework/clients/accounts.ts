import { accountSchema, movementSchema, type Account, type Movement } from "../schemas";
import type { HttpClient } from "../http";

export class AccountsClient {
  constructor(private readonly http: HttpClient) {}

  async list(token: string): Promise<Account[]> {
    const response = await this.http.get("/api/v1/accounts", { token });
    if (response.status() !== 200) {
      throw new Error(`Accounts failed: ${response.status()} ${await response.text()}`);
    }
    return accountSchema.array().parse(await response.json());
  }

  async get(token: string, accountId: string): Promise<Account> {
    const response = await this.http.get(`/api/v1/accounts/${accountId}`, { token });
    if (response.status() !== 200) {
      throw new Error(`Account failed: ${response.status()} ${await response.text()}`);
    }
    return accountSchema.parse(await response.json());
  }

  async movements(token: string, accountId: string): Promise<Movement[]> {
    const response = await this.http.get(`/api/v1/accounts/${accountId}/movements`, { token });
    if (response.status() !== 200) {
      throw new Error(`Movements failed: ${response.status()} ${await response.text()}`);
    }
    return movementSchema.array().parse(await response.json());
  }

  getRaw(token: string | undefined, accountId: string) {
    return this.http.get(`/api/v1/accounts/${accountId}`, { token });
  }
}
