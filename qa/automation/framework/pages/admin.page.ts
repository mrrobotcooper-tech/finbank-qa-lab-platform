import type { Page } from "@playwright/test";

export class AdminPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/admin");
  }

  heading() {
    return this.page.getByTestId("admin-heading");
  }

  usersTable() {
    return this.page.getByTestId("admin-users");
  }

  indicators() {
    return this.page.getByTestId("admin-indicators");
  }

  accountStatus(accountNumber: string) {
    return this.page.getByTestId(`admin-account-status-${accountNumber}`);
  }

  toggle(accountNumber: string) {
    return this.page.getByTestId(`admin-toggle-${accountNumber}`);
  }
}
