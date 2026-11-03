import { Given, Then, When } from "@cucumber/cucumber";
import { expect } from "@playwright/test";

import { BRUNO_CHECKING } from "../../framework/config";
import { uniqueCustomer } from "../../framework/factory";
import { provisionFundedCustomer } from "../../framework/provision";
import { auditForEntity, ledgerForOperation, money } from "../../framework/sql";
import type { FinbankWorld } from "../support/world";

Given(
  "un cliente de laboratorio fondeado con {int} centavos",
  async function (this: FinbankWorld, amount: number) {
    this.draft = uniqueCustomer("bdd");
    const created = await provisionFundedCustomer(this.api(), this.draft, amount);
    this.user = created.user;
    this.session = created.session;
    this.account = created.account;
    this.fundedAmount = amount;
  },
);

When(
  "transfiere {int} centavos a la cuenta corriente de Bruno",
  async function (this: FinbankWorld, amount: number) {
    if (!this.session || !this.account) {
      throw new Error("Falta sesión de cliente");
    }
    this.transfer = await this.transfers.create(this.session.access_token, {
      source_account_id: this.account.id,
      destination_account_number: BRUNO_CHECKING,
      amount,
      currency: "ARS",
    });
  },
);

When(
  "transfiere {int} centavos a Bruno dos veces con la misma clave de idempotencia",
  async function (this: FinbankWorld, amount: number) {
    if (!this.session || !this.account) {
      throw new Error("Falta sesión de cliente");
    }
    const key = crypto.randomUUID();
    const payload = {
      source_account_id: this.account.id,
      destination_account_number: BRUNO_CHECKING,
      amount,
      currency: "ARS",
    };
    const first = await this.transfers.create(this.session.access_token, payload, key);
    const second = await this.transfers.create(this.session.access_token, payload, key);
    this.transfer = first;
    this.lastStatus = first.id === second.id ? 1 : 0;
    expect(second.id).toBe(first.id);
  },
);

Then("la transferencia queda {string}", function (this: FinbankWorld, status: string) {
  expect(this.transfer?.status).toBe(status);
});

Then("su saldo disponible es {int}", async function (this: FinbankWorld, expected: number) {
  if (!this.session || !this.account) {
    throw new Error("Falta cuenta");
  }
  const account = await this.accounts.get(this.session.access_token, this.account.id);
  expect(account.available_balance).toBe(expected);
});

Then("el motivo de rechazo es {string}", function (this: FinbankWorld, reason: string) {
  expect(this.transfer?.rejection_reason).toBe(reason);
});

Then(
  "el ledger tiene débito y crédito por {int} centavos",
  async function (this: FinbankWorld, amount: number) {
    if (!this.transfer) {
      throw new Error("Falta transferencia");
    }
    const rows = await ledgerForOperation(this.sqlPool(), this.transfer.id);
    expect(rows).toHaveLength(2);
    const debit = rows.find((row) => row.direction === "DEBIT");
    const credit = rows.find((row) => row.direction === "CREDIT");
    expect(money(debit?.amount ?? -1)).toBe(amount);
    expect(money(credit?.amount ?? -1)).toBe(amount);
    expect(debit?.operation_type).toBe("TRANSFER");
  },
);

Then(
  "existe un evento de auditoría transfer.created sin usar GET de auditoría",
  async function (this: FinbankWorld) {
    if (!this.transfer || !this.user) {
      throw new Error("Falta transferencia");
    }
    const events = await auditForEntity(this.sqlPool(), this.transfer.id, "transfer.created");
    expect(events).toHaveLength(1);
    const event = events[0];
    expect(event?.actor_user_id).toBe(this.user.id);
    expect(event?.entity_type).toBe("transfer");
    expect(event?.correlation_id).toBe(this.transfer.correlation_id);
    expect(event?.after_state).toMatchObject({ status: "COMPLETED" });
    expect(event?.created_at).toBeTruthy();
  },
);

Then("el ledger de esa operación está vacío", async function (this: FinbankWorld) {
  if (!this.transfer) {
    throw new Error("Falta transferencia");
  }
  const rows = await ledgerForOperation(this.sqlPool(), this.transfer.id);
  expect(rows).toHaveLength(0);
});

Then("ambas respuestas comparten el mismo identificador", function (this: FinbankWorld) {
  expect(this.lastStatus).toBe(1);
  expect(this.transfer?.id).toBeTruthy();
});

Then(
  "el ledger de esa operación tiene exactamente {int} asientos",
  async function (this: FinbankWorld, count: number) {
    if (!this.transfer) {
      throw new Error("Falta transferencia");
    }
    const rows = await ledgerForOperation(this.sqlPool(), this.transfer.id);
    expect(rows).toHaveLength(count);
  },
);
