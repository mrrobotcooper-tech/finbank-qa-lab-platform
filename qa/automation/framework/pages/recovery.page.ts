import type { Page } from "@playwright/test";

export class RecoveryPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/recovery");
    await this.page.getByTestId("recovery-form").waitFor();
  }

  async submit(email: string): Promise<void> {
    await this.page.getByTestId("recovery-email").fill(email);
    await this.page.getByTestId("recovery-submit").click();
  }

  status() {
    return this.page.getByTestId("recovery-status");
  }
}
