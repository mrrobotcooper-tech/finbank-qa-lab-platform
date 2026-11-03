export type User = {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  role: "CUSTOMER" | "SUPPORT" | "ADMIN" | string;
  status: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type Account = {
  id: string;
  account_number: string;
  type: string;
  currency: string;
  status: string;
  available_balance: number;
  held_balance: number;
  daily_transfer_limit: number;
  per_operation_limit: number;
};

export type Movement = {
  id: string;
  operation_id: string;
  operation_type: string;
  direction: string;
  amount: number;
  currency: string;
  balance_after: number;
  description: string | null;
  created_at: string;
};

export type Transfer = {
  id: string;
  source_account_id: string;
  destination_account_id: string;
  amount: number;
  currency: string;
  status: string;
  rejection_reason: string | null;
  correlation_id: string;
  created_at: string;
};

export type Payment = {
  id: string;
  account_id: string;
  payment_type: string;
  payee: string;
  amount: number;
  currency: string;
  status: string;
  rejection_reason: string | null;
  scheduled_at: string | null;
  created_at: string;
};
