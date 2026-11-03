import { CUSTOMER_PASSWORD } from "./config";

export type CustomerDraft = {
  email: string;
  password: string;
  fullName: string;
};

export function uniqueCustomer(prefix = "qa"): CustomerDraft {
  const token = crypto.randomUUID().replaceAll("-", "").slice(0, 12);
  return {
    email: `${prefix}+${token}@finbank.test`,
    password: CUSTOMER_PASSWORD,
    fullName: `QA ${prefix} ${token}`,
  };
}
