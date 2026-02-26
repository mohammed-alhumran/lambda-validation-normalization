# Serverless Event Processing (Local Lambda Simulation)

A Python implementation of a Lambda-style event handler that validates, normalizes, and processes three types of cloud events: user signups, payments, and file uploads.

## Overview

This project simulates AWS Lambda event processing locally. It handles incoming events, validates their structure and content, normalizes data for consistency, and returns standardized JSON responses.

## Supported Event Types

### 1. USER_SIGNUP
Processes user registration events.

**Required Fields:**
- `user_id` (int)
- `email` (str) - must be valid email format
- `plan` (str) - one of: `free`, `pro`, `edu`

**Normalization:**
- `email` → lowercase
- `plan` → lowercase

**Output:**
```json
{
  "status": "ok",
  "message": "Signup processed",
  "data": {
    "user_id": 2041,
    "email": "student.one@school.edu.bh",
    "plan": "edu",
    "welcome_email_subject": "Welcome to the edu plan!"
  },
  "errors": []
}
```

### 2. PAYMENT
Processes payment transactions.

**Required Fields:**
- `payment_id` (str)
- `user_id` (int)
- `amount` (float/int) - must be > 0
- `currency` (str) - one of: `BHD`, `USD`, `EUR`

**Normalization:**
- `currency` → uppercase
- `amount` → float rounded to 3 decimals

**Calculations:**
- `fee` = 2% of amount
- `net_amount` = amount - fee

**Output:**
```json
{
  "status": "ok",
  "message": "Payment processed",
  "data": {
    "payment_id": "pay_abc123",
    "user_id": 2041,
    "amount": 12.75,
    "currency": "BHD",
    "fee": 0.255,
    "net_amount": 12.495
  },
  "errors": []
}
```

### 3. FILE_UPLOAD
Processes file upload events and assigns storage classes.

**Required Fields:**
- `file_name` (str)
- `size_bytes` (int) - must be ≥ 0
- `bucket` (str)
- `uploader` (str) - must be valid email

**Normalization:**
- `bucket` → lowercase
- `file_name` → strip spaces
- `uploader` → lowercase

**Storage Class Assignment:**
- `size_bytes < 1,000,000` → `STANDARD`
- `size_bytes < 50,000,000` → `STANDARD_IA`
- `size_bytes ≥ 50,000,000` → `GLACIER`

**Output:**
```json
{
  "status": "ok",
  "message": "Upload processed",
  "data": {
    "file_name": "project_report.pdf",
    "size_bytes": 2450120,
    "bucket": "ncst-uploads",
    "uploader": "student.one@school.edu.bh",
    "storage_class": "STANDARD_IA"
  },
  "errors": []
}
```

## Project Structure

```
├── handler.py              # Main Lambda handler implementation
├── run_local.py            # Local test runner
├── run_proof.txt           # Test execution proof
├── events/                 # Sample event JSON files
│   ├── 01_user_signup_valid.json
│   ├── 02_payment_valid.json
│   ├── 03_file_upload_valid.json
│   ├── 04_user_signup_invalid_email.json
│   ├── 05_payment_invalid_amount.json
│   ├── 06_file_upload_invalid_missing_field.json
│   ├── 07_unknown_type.json
│   └── 08_bad_json_structure.json
└── expected_outputs/       # Expected JSON responses for valid events
    ├── 01_user_signup_expected.json
    ├── 02_payment_expected.json
    └── 03_file_upload_expected.json
```

## Running Locally

### Run all events:
```bash
python run_local.py --all
```

### Run a single event:
```bash
python run_local.py --event events/01_user_signup_valid.json
```

## Error Handling

The handler returns error responses for:
- Missing required fields
- Invalid field types
- Invalid email formats
- Out-of-range values (e.g., negative amount)
- Unsupported event types
- Malformed event structure

Error response format:
```json
{
  "status": "error",
  "message": "Event rejected",
  "data": null,
  "errors": ["Error message 1", "Error message 2"]
}
```

## Implementation Details

- **Validation:** All required fields are checked before processing
- **Type Checking:** Strict type validation for all inputs
- **Email Validation:** Uses regex pattern `^[^@\s]+@[^@\s]+\.[^@\s]+$`
- **Normalization:** Applied before validation comparisons
- **Calculations:** All numeric values rounded to 3 decimal places
- **JSON Serialization:** All responses are JSON-serializable (dict, list, strings, numbers)