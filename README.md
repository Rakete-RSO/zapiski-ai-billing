# Billing Service API Documentation

This API provides a billing service powered by Stripe. It processes payments for users by creating a Stripe payment intent for a specified customer.

- To setup python packages and start the server (prerequisite: `poetry`):
  - `poetry install`
  - `cp .example.env .env`
  - `poetry run uvicorn src.main:app --reload --port 8004`


## **Endpoints**

### **1. Process Billing**
- **URL**: `/bill`
- **Method**: `GET`
- **Description**: Processes a billing transaction for a customer using Stripe.

#### **Parameters**
| Parameter | Type       | Required | Description                          |
|-----------|------------|----------|--------------------------------------|
| `username` | `string`   | Yes      | The username of the customer         |
| `email`    | `EmailStr` | Yes      | The email address of the customer    |

#### **Request Example**
```bash
GET /bill?username=johndoe&email=johndoe@example.com