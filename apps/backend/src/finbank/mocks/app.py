from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FinBank mocks", version="0.2.0")


class ChargeRequest(BaseModel):
    amount: int
    currency: str
    reference: str
    payee: str = ""


class NotificationRequest(BaseModel):
    channel: str = "EMAIL"
    template: str
    user_id: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "finbank-mocks"}


@app.post("/charges")
def charges(payload: ChargeRequest) -> dict[str, str]:
    if payload.payee.strip().upper() == "REJECT":
        return {
            "status": "rejected",
            "reason": "GATEWAY_REJECTED",
            "reference": payload.reference,
        }
    return {"status": "approved", "reference": payload.reference}


@app.post("/notifications/email")
def send_email(_payload: NotificationRequest) -> dict[str, str]:
    return {"status": "sent"}


@app.post("/notifications/sms")
def send_sms(_payload: NotificationRequest) -> dict[str, str]:
    return {"status": "sent"}
