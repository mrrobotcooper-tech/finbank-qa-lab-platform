import {
  accountSchema,
  indicatorsSchema,
  paymentSchema,
  transferSchema,
  userSchema,
  type Account,
  type User,
} from "../schemas";
import type { HttpClient } from "../http";

export class AdminClient {
  constructor(private readonly http: HttpClient) {}

  async listUsers(token: string): Promise<User[]> {
    const response = await this.http.get("/api/v1/admin/users", { token });
    if (response.status() !== 200) {
      throw new Error(`Admin users failed: ${response.status()} ${await response.text()}`);
    }
    return userSchema.array().parse(await response.json());
  }

  listUsersRaw(token: string | undefined) {
    return this.http.get("/api/v1/admin/users", { token });
  }

  async updateUser(
    token: string,
    userId: string,
    payload: { status?: string; role?: string },
  ): Promise<User> {
    const response = await this.http.patch(`/api/v1/admin/users/${userId}`, { token, data: payload });
    if (response.status() !== 200) {
      throw new Error(`Admin user update failed: ${response.status()} ${await response.text()}`);
    }
    return userSchema.parse(await response.json());
  }

  updateUserRaw(token: string | undefined, userId: string, payload: { status?: string; role?: string }) {
    return this.http.patch(`/api/v1/admin/users/${userId}`, { token, data: payload });
  }

  async updateAccount(token: string, accountId: string, status: string): Promise<Account> {
    const response = await this.http.patch(`/api/v1/admin/accounts/${accountId}`, {
      token,
      data: { status },
    });
    if (response.status() !== 200) {
      throw new Error(`Admin account update failed: ${response.status()} ${await response.text()}`);
    }
    return accountSchema.parse(await response.json());
  }

  updateAccountRaw(token: string | undefined, accountId: string, status: string) {
    return this.http.patch(`/api/v1/admin/accounts/${accountId}`, { token, data: { status } });
  }

  async operations(token: string) {
    const response = await this.http.get("/api/v1/admin/operations", { token });
    if (response.status() !== 200) {
      throw new Error(`Admin operations failed: ${response.status()} ${await response.text()}`);
    }
    const body = (await response.json()) as { transfers: unknown; payments: unknown };
    return {
      transfers: transferSchema.array().parse(body.transfers),
      payments: paymentSchema.array().parse(body.payments),
    };
  }

  async indicators(token: string) {
    const response = await this.http.get("/api/v1/admin/indicators", { token });
    if (response.status() !== 200) {
      throw new Error(`Admin indicators failed: ${response.status()} ${await response.text()}`);
    }
    return indicatorsSchema.parse(await response.json());
  }

  operationsRaw(token: string | undefined) {
    return this.http.get("/api/v1/admin/operations", { token });
  }

  async operationTrace(token: string, transferId: string) {
    const response = await this.http.get(`/api/v1/admin/operations/${transferId}`, { token });
    if (response.status() !== 200) {
      throw new Error(`Admin trace failed: ${response.status()} ${await response.text()}`);
    }
    return (await response.json()) as {
      id: string;
      status: string;
      amount: number;
      currency: string;
      correlation_id: string;
      created_at: string | null;
    };
  }
}
