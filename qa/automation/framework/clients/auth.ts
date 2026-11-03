import {
  activitySchema,
  notificationSchema,
  tokenSchema,
  userSchema,
  type TokenResponse,
  type User,
} from "../schemas";
import type { HttpClient } from "../http";

export class AuthClient {
  constructor(private readonly http: HttpClient) {}

  async register(input: { email: string; password: string; fullName: string }): Promise<User> {
    const response = await this.registerRaw(input);
    if (response.status() !== 201) {
      throw new Error(`Register failed: ${response.status()} ${await response.text()}`);
    }
    return userSchema.parse(await response.json());
  }

  registerRaw(input: { email: string; password: string; fullName: string }) {
    return this.http.post("/api/v1/auth/register", {
      data: {
        email: input.email,
        password: input.password,
        full_name: input.fullName,
      },
    });
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await this.loginRaw(email, password);
    if (response.status() !== 200) {
      throw new Error(`Login failed: ${response.status()} ${await response.text()}`);
    }
    return tokenSchema.parse(await response.json());
  }

  loginRaw(email: string, password: string) {
    return this.http.post("/api/v1/auth/login", { data: { email, password } });
  }

  async me(token: string): Promise<User> {
    const response = await this.http.get("/api/v1/me", { token });
    if (response.status() !== 200) {
      throw new Error(`Me failed: ${response.status()} ${await response.text()}`);
    }
    return userSchema.parse(await response.json());
  }

  logout() {
    return this.http.post("/api/v1/auth/logout");
  }

  refresh() {
    return this.http.post("/api/v1/auth/refresh");
  }

  recovery(email: string) {
    return this.http.post("/api/v1/auth/recovery", { data: { email } });
  }

  confirmRecovery(token: string, password: string) {
    return this.http.post("/api/v1/auth/recovery/confirm", { data: { token, password } });
  }

  async updateProfile(token: string, payload: { full_name?: string; phone?: string }): Promise<User> {
    const response = await this.http.patch("/api/v1/me", { token, data: payload });
    if (response.status() !== 200) {
      throw new Error(`Profile failed: ${response.status()} ${await response.text()}`);
    }
    return userSchema.parse(await response.json());
  }

  async activity(token: string) {
    const response = await this.http.get("/api/v1/me/activity", { token });
    if (response.status() !== 200) {
      throw new Error(`Activity failed: ${response.status()} ${await response.text()}`);
    }
    return activitySchema.array().parse(await response.json());
  }

  async notifications(token: string) {
    const response = await this.http.get("/api/v1/me/notifications", { token });
    if (response.status() !== 200) {
      throw new Error(`Notifications failed: ${response.status()} ${await response.text()}`);
    }
    return notificationSchema.array().parse(await response.json());
  }
}
