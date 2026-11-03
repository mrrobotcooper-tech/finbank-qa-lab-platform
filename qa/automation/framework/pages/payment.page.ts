import { expect, type Page } from "@playwright/test";

export class PaymentPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/payments");
    await this.page.getByTestId("payment-form").waitFor();
    await expect(this.page.getByTestId("payment-submit")).toBeEnabled();
  }

  async submit(payee: string, amount: string, type = "SERVICE"): Promise<void> {
    await this.page.getByTestId("payment-type").selectOption(type);
    await this.page.getByTestId("payment-payee").fill(payee);
    await this.page.getByTestId("payment-amount").fill(amount);
    await this.page.getByTestId("payment-submit").click();
    await Promise.race([this.result().waitFor(), this.error().waitFor()]);
  }

  result() {
    return this.page.getByTestId("payment-result");
  }

  error() {
    return this.page.getByTestId("payment-error");
  }
}
