import { expect, type Page } from "@playwright/test";

export class TransferPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/transfers");
    await this.page.getByTestId("transfer-form").waitFor();
  }

  submitButton() {
    return this.page.getByTestId("transfer-submit");
  }

  async submit(destination: string, amount: string): Promise<void> {
    await expect(this.submitButton()).toBeEnabled();
    await this.page.getByTestId("transfer-destination").fill(destination);
    await this.page.getByTestId("transfer-amount").fill(amount);
    await this.submitButton().click();
    await Promise.race([this.result().waitFor(), this.error().waitFor()]);
  }

  result() {
    return this.page.getByTestId("transfer-result");
  }

  error() {
    return this.page.getByTestId("transfer-error");
  }
}
