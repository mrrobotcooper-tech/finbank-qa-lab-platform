import type { Page } from "@playwright/test";

import type { CustomerDraft } from "../factory";

export class RegisterPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/register");
    await this.page.getByTestId("register-form").waitFor();
  }

  async submit(draft: CustomerDraft): Promise<void> {
    await this.page.getByTestId("register-full-name").fill(draft.fullName);
    await this.page.getByTestId("register-email").fill(draft.email);
    await this.page.getByTestId("register-password").fill(draft.password);
    await this.page.getByTestId("register-submit").click();
    await this.page.getByTestId("login-form").waitFor();
  }
}
