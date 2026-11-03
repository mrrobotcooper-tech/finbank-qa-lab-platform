import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../auth/AuthContext";
import { LoginPage } from "./LoginPage";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Not authenticated" }),
    }),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("LoginPage", () => {
  it("muestra el formulario de ingreso y las cuentas demo", async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>,
    );
    expect(await screen.findByTestId("login-form")).toBeInTheDocument();
    expect(screen.getByTestId("login-email")).toHaveValue("ana@finbank.test");
    expect(screen.getByText("ana@finbank.test")).toBeInTheDocument();
  });
});
