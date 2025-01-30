import os
from fastapi import FastAPI, HTTPException
from pydantic import EmailStr
import stripe

stripe.api_key = os.getenv("STRIPE_KEY")

app = FastAPI()


@app.get("/bill")
async def process_billing(username: str, email: EmailStr):
    """
    Process a billing transaction for a user via Stripe

    Args:
        username (str): The username of the customer
        email (EmailStr): The email address of the customer

    Returns:
        dict: A dictionary containing the billing transaction details
    """
    try:
        # Create a customer in Stripe (if not already exists)
        customer = stripe.Customer.list(email=email).data

        if not customer:
            raise HTTPException(
                404, detail="Billable entity not found, make sure you registered!"
            )
        else:
            customer = customer[0]

        # Create a payment intent (adjust amount and currency as needed)
        payment_intent = stripe.PaymentIntent.create(
            amount=13000,
            currency="eur",
            customer=customer.id,
            payment_method_types=["card"],
            description=f"Billing for {username}",
        )

        return {
            "status": "success",
            "customer_id": customer.id,
            "payment_intent_id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
        }

    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health-check")
def health_check():
    # return status 200
    return {"status": "ok"}

# Additional configuration for Stripe error handling
@app.exception_handler(stripe.error.StripeError)
async def stripe_exception_handler(request, exc):
    return {"status": "error", "message": str(exc)}
