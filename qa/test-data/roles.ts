/** Perfiles de rol reutilizables. Las identidades únicas viven en factory.ts. */
export const roleProfiles = {
  customerHappy: { role: "CUSTOMER", password: "Customer1!" },
  customerZero: { role: "CUSTOMER", password: "Customer1!" },
  support: { role: "SUPPORT", password: "SupportPassw0rd" },
  admin: { role: "ADMIN", password: "AdminPassw0rd" },
} as const;
