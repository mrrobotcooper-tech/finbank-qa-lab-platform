import { World, setWorldConstructor, type IWorldOptions } from "@cucumber/cucumber";
import type { APIRequestContext } from "@playwright/test";
import type { Pool } from "pg";

import { AccountsClient } from "../../framework/clients/accounts";
import { AuthClient } from "../../framework/clients/auth";
import { PaymentsClient } from "../../framework/clients/payments";
import { TransfersClient } from "../../framework/clients/transfers";
import type { CustomerDraft } from "../../framework/factory";
import { HttpClient } from "../../framework/http";
import type { Account, TokenResponse, Transfer, User } from "../../framework/schemas";
import { createQaPool } from "../../framework/sql";

export class FinbankWorld extends World {
  apiContext!: APIRequestContext;
  http!: HttpClient;
  auth!: AuthClient;
  accounts!: AccountsClient;
  transfers!: TransfersClient;
  payments!: PaymentsClient;
  pool: Pool | undefined;
  draft: CustomerDraft | undefined;
  user: User | undefined;
  session: TokenResponse | undefined;
  account: Account | undefined;
  transfer: Transfer | undefined;
  lastStatus = 0;
  fundedAmount = 0;

  constructor(options: IWorldOptions) {
    super(options);
  }

  api() {
    return {
      http: this.http,
      auth: this.auth,
      accounts: this.accounts,
      transfers: this.transfers,
    };
  }

  sqlPool(): Pool {
    if (!this.pool) {
      this.pool = createQaPool();
    }
    return this.pool;
  }
}

setWorldConstructor(FinbankWorld);
