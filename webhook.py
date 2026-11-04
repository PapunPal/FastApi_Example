from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Payment Webhook Receiver",
    description="FastAPI application to receive payment events",
    version="1.0"
)

# Temporary storage for received webhook events
received_events = {}


# Define the expected webhook JSON structure
class PaymentWebhook(BaseModel):
    event_id: str
    event_type: str
    order_id: str
    customer: str
    amount: float
    currency: str
    payment_status: str


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Payment Webhook Receiver is running"
    }


# Webhook receiver endpoint
@app.post("/webhook/payment")
def receive_payment_webhook(payment: PaymentWebhook):

    # Check whether event was already received
    if payment.event_id in received_events:
        return {
            "message": "Duplicate event received",
            "event_id": payment.event_id,
            "status": "ALREADY_PROCESSED"
        }

    # Validate event type
    if payment.event_type != "payment.success":
        raise HTTPException(
            status_code=400,
            detail="Unsupported payment event type"
        )

    # Validate payment status
    if payment.payment_status != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail="Payment is not successful"
        )

    # Store received event
    received_events[payment.event_id] = {
        "event_id": payment.event_id,
        "order_id": payment.order_id,
        "customer": payment.customer,
        "amount": payment.amount,
        "currency": payment.currency,
        "payment_status": payment.payment_status,
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    print("\n========== WEBHOOK RECEIVED ==========")
    print("Event ID:", payment.event_id)
    print("Order ID:", payment.order_id)
    print("Customer:", payment.customer)
    print("Amount:", payment.amount)
    print("Payment Status:", payment.payment_status)
    print("======================================\n")

    return {
        "message": "Webhook received successfully",
        "event_id": payment.event_id,
        "status": "PROCESSED"
    }


# Get all received webhook events
@app.get("/webhook/events")
def get_all_events():

    return {
        "total_events": len(received_events),
        "events": list(received_events.values())
    }


# Get a particular webhook event
@app.get("/webhook/events/{event_id}")
def get_event(event_id: str):

    if event_id not in received_events:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return received_events[event_id]
