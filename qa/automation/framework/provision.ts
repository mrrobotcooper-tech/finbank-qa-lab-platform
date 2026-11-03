import { ANA_CHECKING, qaConfig } from "./config";
import type { AccountsClient } from "./clients/accounts";
import type { AuthClient } from "./clients/auth";
import type { TransfersClient } from "./clients/transfers";
import type { CustomerDraft } from "./factory";
import type { Account, TokenResponse, Transfer, User } from "./schemas";

export type BankingApi = {
  auth: AuthClient;
  accounts: AccountsClient;
  transfers: TransfersClient;
};

export type ProvisionedCustomer = {
  draft: CustomerDraft;
  user: User;
  session: TokenResponse;
  account: Account;
};

export async function registerAndLogin(
  api: BankingApi,
  draft: CustomerDraft,
): Promise<ProvisionedCustomer> {
  const user = await api.auth.register(draft);
  const session = await api.auth.login(draft.email, draft.password);
  const accounts = await api.accounts.list(session.access_token);
  const account = accounts[0];
  if (!account) {
    throw new Error("El cliente registrado no tiene cuenta");
  }
  return { draft, user, session, account };
}

export async function fundFromAna(
  api: BankingApi,
  destinationAccountNumber: string,
  amount: number,
): Promise<Transfer> {
  const ana = await api.auth.login(qaConfig.seed.ana.email, qaConfig.seed.ana.password);
  const accounts = await api.accounts.list(ana.access_token);
  const source = accounts.find((item) => item.account_number === ANA_CHECKING);
  if (!source) {
    throw new Error("No está la cuenta ARS de Ana");
  }
  return api.transfers.create(ana.access_token, {
    source_account_id: source.id,
    destination_account_number: destinationAccountNumber,
    amount,
    currency: "ARS",
  });
}

export async function provisionFundedCustomer(
  api: BankingApi,
  draft: CustomerDraft,
  amount: number,
): Promise<ProvisionedCustomer & { fundedAmount: number }> {
  const created = await registerAndLogin(api, draft);
  const funding = await fundFromAna(api, created.account.account_number, amount);
  if (funding.status !== "COMPLETED") {
    throw new Error(`No se pudo fondear al cliente QA: ${funding.status} ${funding.rejection_reason}`);
  }
  const account = await api.accounts.get(created.session.access_token, created.account.id);
  return { ...created, account, fundedAmount: amount };
}
