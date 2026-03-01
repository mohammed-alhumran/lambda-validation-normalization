"""
PL202 — Serverless Event Processing (Local Lambda Simulation)
Day 1 (45 min) — Individual Task
Mohammed Alhumran 
You will implement a Lambda-style handler:
    def handler(event, context): -> dict
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import re


ALLOWED_TYPES = {"USER_SIGNUP", "PAYMENT", "FILE_UPLOAD"}


def _err(*msgs: str) -> Dict[str, Any]:
    """Create a standard error response."""
    return {
        "status": "error",
        "message": "Event rejected",
        "data": None,
        "errors": list(msgs),
    }


def _ok(message: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a standard ok response."""
    return {
        "status": "ok",
        "message": message,
        "data": data,
        "errors": [],
    }


def _is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))


def handler(event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Main Lambda-style handler."""

    if not isinstance(event, dict):
        return _err("Event must be a dictionary")

    if "type" not in event:
        return _err("Missing required field: type")

    event_type = event["type"]

    if event_type not in ALLOWED_TYPES:
        return _err(f"Unsupported event type: {event_type}")

    if event_type == "USER_SIGNUP":
        return handle_user_signup(event)
    elif event_type == "PAYMENT":
        return handle_payment(event)
    elif event_type == "FILE_UPLOAD":
        return handle_file_upload(event)

    return _err("Unhandled event type")


def handle_user_signup(event: Dict[str, Any]) -> Dict[str, Any]:

    required = ["user_id", "email", "plan"]
    for field in required:
        if field not in event:
            return _err(f"Missing required field: {field}")

    user_id = event["user_id"]
    email = event["email"]
    plan = event["plan"]

    if not isinstance(user_id, int):
        return _err("user_id must be an integer")

    if not isinstance(email, str):
        return _err("email must be a string")

    if not isinstance(plan, str):
        return _err("plan must be a string")

    email = email.lower()
    plan = plan.lower()

    if not _is_email(email):
        return _err("Invalid email format")

    if plan not in {"free", "pro", "edu"}:
        return _err("Invalid plan value")

    data = {
        "user_id": user_id,
        "email": email,
        "plan": plan,
        "welcome_email_subject": f"Welcome to the {plan} plan!",
    }

    return _ok("Signup processed", data)


def handle_payment(event: Dict[str, Any]) -> Dict[str, Any]:

    required = ["payment_id", "user_id", "amount", "currency"]
    for field in required:
        if field not in event:
            return _err(f"Missing required field: {field}")

    payment_id = event["payment_id"]
    user_id = event["user_id"]
    amount = event["amount"]
    currency = event["currency"]

    if not isinstance(payment_id, str):
        return _err("payment_id must be a string")

    if not isinstance(user_id, int):
        return _err("user_id must be an integer")

    if not isinstance(amount, (int, float)):
        return _err("amount must be a number")

    if not isinstance(currency, str):
        return _err("currency must be a string")

    if amount <= 0:
        return _err("amount must be greater than 0")

    currency = currency.upper()

    if currency not in {"BHD", "USD", "EUR"}:
        return _err("Invalid currency")

    amount = round(float(amount), 3)
    fee = round(amount * 0.02, 3)
    net_amount = round(amount - fee, 3)

    data = {
        "payment_id": payment_id,
        "user_id": user_id,
        "amount": amount,
        "currency": currency,
        "fee": fee,
        "net_amount": net_amount,
    }

    return _ok("Payment processed", data)


def handle_file_upload(event: Dict[str, Any]) -> Dict[str, Any]:

    required = ["file_name", "size_bytes", "bucket", "uploader"]
    for field in required:
        if field not in event:
            return _err(f"Missing required field: {field}")

    file_name = event["file_name"]
    size_bytes = event["size_bytes"]
    bucket = event["bucket"]
    uploader = event["uploader"]

    if not isinstance(file_name, str):
        return _err("file_name must be a string")

    if not isinstance(size_bytes, int):
        return _err("size_bytes must be an integer")

    if size_bytes < 0:
        return _err("size_bytes must be >= 0")

    if not isinstance(bucket, str):
        return _err("bucket must be a string")

    if not isinstance(uploader, str):
        return _err("uploader must be a string")

    uploader = uploader.lower()

    if not _is_email(uploader):
        return _err("Invalid uploader email")

    file_name = file_name.strip()
    bucket = bucket.lower()

    if size_bytes < 1_000_000:
        storage_class = "STANDARD"
    elif size_bytes < 50_000_000:
        storage_class = "STANDARD_IA"
    else:
        storage_class = "GLACIER"

    data = {
        "file_name": file_name,
        "size_bytes": size_bytes,
        "bucket": bucket,
        "uploader": uploader,
        "storage_class": storage_class,
    }

    return _ok("Upload processed", data)
