import { z } from "zod";

export const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().min(3),
  full_name: z.string(),
  phone: z.string().nullable(),
  role: z.enum(["CUSTOMER", "SUPPORT", "ADMIN"]),
  status: z.string(),
});

export const tokenSchema = z.object({
  access_token: z.string().min(10),
  token_type: z.string(),
  user: userSchema,
});

export const accountSchema = z.object({
  id: z.string().uuid(),
  account_number: z.string().min(6),
  type: z.string(),
  currency: z.string(),
  status: z.string(),
  available_balance: z.number().int(),
  held_balance: z.number().int(),
  daily_transfer_limit: z.number().int(),
  per_operation_limit: z.number().int(),
});

export const healthSchema = z.object({
  status: z.literal("ok"),
  service: z.string().optional(),
  environment: z.string().optional(),
  correlation_id: z.string().optional(),
});

export const readySchema = z.object({
  status: z.enum(["ok", "degraded"]),
  correlation_id: z.string(),
  components: z.array(
    z.object({
      name: z.string(),
      status: z.enum(["up", "down"]),
      detail: z.string().optional(),
    }),
  ),
});

export const errorSchema = z.object({
  detail: z.union([z.string(), z.array(z.unknown())]),
  code: z.string().optional(),
});

export const movementSchema = z.object({
  id: z.string().uuid(),
  operation_id: z.string().uuid(),
  operation_type: z.string(),
  direction: z.enum(["DEBIT", "CREDIT"]),
  amount: z.number().int(),
  currency: z.string(),
  balance_after: z.number().int(),
  description: z.string().nullable(),
  created_at: z.string(),
});

export const transferSchema = z.object({
  id: z.string().uuid(),
  source_account_id: z.string().uuid(),
  destination_account_id: z.string().uuid(),
  amount: z.number().int(),
  currency: z.string(),
  status: z.string(),
  rejection_reason: z.string().nullable(),
  correlation_id: z.string(),
  created_at: z.string(),
});

export const paymentSchema = z.object({
  id: z.string().uuid(),
  account_id: z.string().uuid(),
  payment_type: z.string(),
  payee: z.string(),
  amount: z.number().int(),
  currency: z.string(),
  status: z.string(),
  rejection_reason: z.string().nullable(),
  scheduled_at: z.string().nullable(),
  created_at: z.string(),
});

export const activitySchema = z.object({
  id: z.string().uuid(),
  action: z.string(),
  detail: z.string().nullable(),
  created_at: z.string(),
});

export const notificationSchema = z.object({
  id: z.string().uuid(),
  channel: z.string(),
  template: z.string(),
  payload: z.record(z.unknown()),
  status: z.string(),
  created_at: z.string(),
});

export const indicatorsSchema = z.object({
  users: z.number().int(),
  accounts: z.number().int(),
  completed_transfers: z.number().int(),
});

export type User = z.infer<typeof userSchema>;
export type TokenResponse = z.infer<typeof tokenSchema>;
export type Account = z.infer<typeof accountSchema>;
export type Transfer = z.infer<typeof transferSchema>;
export type Payment = z.infer<typeof paymentSchema>;
export type Movement = z.infer<typeof movementSchema>;
