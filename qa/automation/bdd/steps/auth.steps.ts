import { Given, Then, When } from "@cucumber/cucumber";
import { expect } from "@playwright/test";

import { uniqueCustomer } from "../../framework/factory";
import { registerAndLogin } from "../../framework/provision";
import type { FinbankWorld } from "../support/world";

Given("un email de laboratorio único", function (this: FinbankWorld) {
  this.draft = uniqueCustomer("bdd");
});

Given("un cliente ya registrado", async function (this: FinbankWorld) {
  this.draft = uniqueCustomer("bdd");
  const created = await registerAndLogin(this.api(), this.draft);
  this.user = created.user;
  this.session = created.session;
  this.account = created.account;
});

When("me registro con contraseña válida", async function (this: FinbankWorld) {
  if (!this.draft) {
    throw new Error("Falta el draft del cliente");
  }
  this.user = await this.auth.register(this.draft);
});

When("intento registrarme otra vez con el mismo email", async function (this: FinbankWorld) {
  if (!this.draft) {
    throw new Error("Falta el draft del cliente");
  }
  const response = await this.auth.registerRaw(this.draft);
  this.lastStatus = response.status();
});

When("intento autenticarme con una clave incorrecta", async function (this: FinbankWorld) {
  if (!this.draft) {
    throw new Error("Falta el draft del cliente");
  }
  const response = await this.auth.loginRaw(this.draft.email, "WrongPassw0rd");
  this.lastStatus = response.status();
});

Then("el usuario queda con rol {string}", function (this: FinbankWorld, role: string) {
  expect(this.user?.role).toBe(role);
});

Then("puedo autenticarme y ver una cuenta ARS", async function (this: FinbankWorld) {
  if (!this.draft || !this.user) {
    throw new Error("Falta el usuario registrado");
  }
  this.session = await this.auth.login(this.draft.email, this.draft.password);
  expect(this.session.user.id).toBe(this.user.id);
  const accounts = await this.accounts.list(this.session.access_token);
  expect(accounts[0]?.currency).toBe("ARS");
});

Then("la API responde {int}", function (this: FinbankWorld, status: number) {
  expect(this.lastStatus).toBe(status);
});
