import { test as base, expect } from "@playwright/test";

import { AccountsClient } from "./clients/accounts";
import { AdminClient } from "./clients/admin";
import { AuthClient } from "./clients/auth";
import { PaymentsClient } from "./clients/payments";
import { TransfersClient } from "./clients/transfers";
import { qaConfig } from "./config";
import { uniqueCustomer, type CustomerDraft } from "./factory";
import { HttpClient } from "./http";
import { AccountsPage } from "./pages/accounts.page";
import { AdminPage } from "./pages/admin.page";
import { LoginPage } from "./pages/login.page";
import { PaymentPage } from "./pages/payment.page";
import { ProfilePage } from "./pages/profile.page";
import { RecoveryPage } from "./pages/recovery.page";
import { RegisterPage } from "./pages/register.page";
import { TransferPage } from "./pages/transfer.page";
import type { TokenResponse } from "./schemas";

export type ApiBundle = {
  http: HttpClient;
  auth: AuthClient;
  accounts: AccountsClient;
  transfers: TransfersClient;
  payments: PaymentsClient;
  admin: AdminClient;
};

type Fixtures = {
  api: ApiBundle;
  customerDraft: CustomerDraft;
  seedCustomer: TokenResponse;
  seedAdmin: TokenResponse;
  seedSupport: TokenResponse;
  seedBruno: TokenResponse;
  loginPage: LoginPage;
  accountsPage: AccountsPage;
  registerPage: RegisterPage;
  transferPage: TransferPage;
  paymentPage: PaymentPage;
  adminPage: AdminPage;
  profilePage: ProfilePage;
  recoveryPage: RecoveryPage;
};

export const test = base.extend<Fixtures>({
  api: async ({ request }, use) => {
    const http = new HttpClient(request, qaConfig.apiUrl);
    await use({
      http,
      auth: new AuthClient(http),
      accounts: new AccountsClient(http),
      transfers: new TransfersClient(http),
      payments: new PaymentsClient(http),
      admin: new AdminClient(http),
    });
  },
  customerDraft: async ({}, use) => {
    await use(uniqueCustomer());
  },
  seedCustomer: async ({ api }, use) => {
    const tokens = await api.auth.login(qaConfig.seed.ana.email, qaConfig.seed.ana.password);
    await use(tokens);
  },
  seedAdmin: async ({ api }, use) => {
    const tokens = await api.auth.login(qaConfig.seed.admin.email, qaConfig.seed.admin.password);
    await use(tokens);
  },
  seedSupport: async ({ api }, use) => {
    const tokens = await api.auth.login(qaConfig.seed.support.email, qaConfig.seed.support.password);
    await use(tokens);
  },
  seedBruno: async ({ api }, use) => {
    const tokens = await api.auth.login(qaConfig.seed.bruno.email, qaConfig.seed.bruno.password);
    await use(tokens);
  },
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  accountsPage: async ({ page }, use) => {
    await use(new AccountsPage(page));
  },
  registerPage: async ({ page }, use) => {
    await use(new RegisterPage(page));
  },
  transferPage: async ({ page }, use) => {
    await use(new TransferPage(page));
  },
  paymentPage: async ({ page }, use) => {
    await use(new PaymentPage(page));
  },
  adminPage: async ({ page }, use) => {
    await use(new AdminPage(page));
  },
  profilePage: async ({ page }, use) => {
    await use(new ProfilePage(page));
  },
  recoveryPage: async ({ page }, use) => {
    await use(new RecoveryPage(page));
  },
});

export { expect };
