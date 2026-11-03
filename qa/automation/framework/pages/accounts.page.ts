import type { Page } from "@playwright/test";

export class AccountsPage {
  constructor(private readonly page: Page) {}

  async waitForLoaded(): Promise<void> {
    await this.page.getByTestId("accounts-heading").waitFor();
    await this.page.getByTestId("accounts-table").locator("tbody tr").first().waitFor();
  }

  table() {
    return this.page.getByTestId("accounts-table");
  }

  accountRow(accountNumber: string) {
    return this.page.getByTestId(`account-${accountNumber}`);
  }
}
