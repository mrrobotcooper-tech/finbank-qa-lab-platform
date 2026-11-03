import { After, Before, setDefaultTimeout } from "@cucumber/cucumber";
import { request } from "@playwright/test";

import { AccountsClient } from "../../framework/clients/accounts";
import { AuthClient } from "../../framework/clients/auth";
import { PaymentsClient } from "../../framework/clients/payments";
import { TransfersClient } from "../../framework/clients/transfers";
import { qaConfig } from "../../framework/config";
import { HttpClient } from "../../framework/http";
import type { FinbankWorld } from "./world";

setDefaultTimeout(30_000);

Before(async function (this: FinbankWorld) {
  this.apiContext = await request.newContext();
  this.http = new HttpClient(this.apiContext, qaConfig.apiUrl);
  this.auth = new AuthClient(this.http);
  this.accounts = new AccountsClient(this.http);
  this.transfers = new TransfersClient(this.http);
  this.payments = new PaymentsClient(this.http);
});

After(async function (this: FinbankWorld) {
  if (this.pool) {
    await this.pool.end();
    this.pool = undefined;
  }
  await this.apiContext.dispose();
});
