import { expect, test } from "../framework/fixtures";
import { uniqueCustomer } from "../framework/factory";
import { createQaPool, sqlQuery } from "../framework/sql";

test("NFR-SEC-001 el hash persistido es Argon2 y no el plaintext @security @critical @data", async ({
  api,
}) => {
  const draft = uniqueCustomer("sec");
  const user = await api.auth.register(draft);
  const pool = createQaPool();
  try {
    const rows = await sqlQuery<{ password_hash: string }>(
      pool,
      "SELECT password_hash FROM users WHERE id = $1",
      [user.id],
    );
    const hash = rows[0]?.password_hash ?? "";
    expect(hash.startsWith("$argon2")).toBe(true);
    expect(hash.includes(draft.password)).toBe(false);
    expect(hash.toLowerCase().includes("customer")).toBe(false);
  } finally {
    await pool.end();
  }
});
