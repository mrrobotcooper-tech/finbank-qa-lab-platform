export type SeedUser = {
  email: string;
  password: string;
  role: "CUSTOMER" | "SUPPORT" | "ADMIN";
};

export type QaConfig = {
  baseUrl: string;
  apiUrl: string;
  databaseUrl: string;
  correlationHeader: string;
  seed: {
    ana: SeedUser;
    bruno: SeedUser;
    admin: SeedUser;
    support: SeedUser;
  };
};

function env(name: string, fallback: string): string {
  const value = process.env[name];
  return value && value.length > 0 ? value : fallback;
}

export const qaConfig: QaConfig = {
  baseUrl: env("QA_BASE_URL", "http://localhost:5173"),
  apiUrl: env("QA_API_URL", "http://localhost:8000"),
  databaseUrl: env(
    "QA_DATABASE_URL",
    "postgresql://finbank_qa_reader:change_me_qa@127.0.0.1:15432/finbank",
  ),
  correlationHeader: env("CORRELATION_HEADER", "X-Correlation-ID"),
  seed: {
    ana: {
      email: "ana@finbank.test",
      password: "Customer1!",
      role: "CUSTOMER",
    },
    bruno: {
      email: "bruno@finbank.test",
      password: "Customer1!",
      role: "CUSTOMER",
    },
    admin: {
      email: "admin@finbank.test",
      password: "AdminPassw0rd",
      role: "ADMIN",
    },
    support: {
      email: "support@finbank.test",
      password: "SupportPassw0rd",
      role: "SUPPORT",
    },
  },
};

export const CUSTOMER_PASSWORD = "Customer1!";
export const ANA_CHECKING = "32200000000000000001";
export const ANA_SAVINGS_USD = "32200000000000000002";
export const BRUNO_CHECKING = "32200000000000000003";
export const BRUNO_BLOCKED = "32200000000000000004";
export const CARA_CHECKING = "32200000000000000005";
export const PER_OPERATION_LIMIT = 5_000_000;
export const LOGIN_MAX_ATTEMPTS = 5;
