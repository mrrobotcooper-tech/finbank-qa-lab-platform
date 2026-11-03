import type { Page } from "@playwright/test";

export class LoginPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/login");
    await this.page.getByTestId("login-form").waitFor();
  }

  async login(email: string, password: string): Promise<void> {
    await this.page.getByTestId("login-email").fill(email);
    await this.page.getByTestId("login-password").fill(password);
    await this.page.getByTestId("login-submit").click();
    await Promise.race([
      this.page.getByTestId("nav-logout").waitFor(),
      this.page.getByTestId("login-error").waitFor(),
    ]);
  }

  error() {
    return this.page.getByTestId("login-error");
  }
}
