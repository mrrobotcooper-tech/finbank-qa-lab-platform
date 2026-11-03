"use strict";

const API = process.env.FINBANK_API_URL || "http://127.0.0.1:8000";
const EMAIL = process.env.FINBANK_PERF_EMAIL || "ana@finbank.test";
const PASSWORD = process.env.FINBANK_PERF_PASSWORD || "Customer1!";
const DEST = process.env.FINBANK_PERF_DEST || "32200000000000000003";

let cached = { token: null, sourceId: null };

async function loginPayload() {
  const response = await fetch(`${API}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
  });
  if (!response.ok) {
    throw new Error(`login ${response.status}: ${await response.text()}`);
  }
  const body = await response.json();
  const accountsRes = await fetch(`${API}/api/v1/accounts`, {
    headers: { Authorization: `Bearer ${body.access_token}` },
  });
  if (!accountsRes.ok) {
    throw new Error(`accounts ${accountsRes.status}`);
  }
  const accounts = await accountsRes.json();
  const checking = accounts.find((item) => item.currency === "ARS" && item.type === "CHECKING");
  if (!checking) {
    throw new Error("Ana ARS checking not found");
  }
  return { token: body.access_token, sourceId: checking.id };
}

async function ensureSession() {
  if (!cached.token) {
    cached = await loginPayload();
  }
  return cached;
}

function authenticate(context, _events, done) {
  ensureSession()
    .then((session) => {
      context.vars.token = session.token;
      context.vars.sourceId = session.sourceId;
      context.vars.destCbu = DEST;
      done();
    })
    .catch(done);
}

function setIdempotency(requestParams, context, _ee, next) {
  requestParams.headers = requestParams.headers || {};
  requestParams.headers.Authorization = `Bearer ${context.vars.token}`;
  requestParams.headers["Idempotency-Key"] = `perf-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  requestParams.headers["Content-Type"] = "application/json";
  requestParams.json = {
    source_account_id: context.vars.sourceId,
    destination_account_number: context.vars.destCbu,
    amount: 1,
    currency: "ARS",
  };
  return next();
}

function setBearer(requestParams, context, _ee, next) {
  requestParams.headers = requestParams.headers || {};
  requestParams.headers.Authorization = `Bearer ${context.vars.token}`;
  return next();
}

module.exports = { authenticate, setIdempotency, setBearer };
