import type { Page } from "@playwright/test";

export class ProfilePage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/profile");
    await this.page.getByTestId("profile-form").waitFor();
  }

  async save(fullName: string, phone = ""): Promise<void> {
    await this.page.getByTestId("profile-full-name").fill(fullName);
    await this.page.getByTestId("profile-phone").fill(phone);
    await this.page.getByTestId("profile-submit").click();
  }

  status() {
    return this.page.getByTestId("profile-status");
  }
}
