from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from models import Subscription, User

# Database URL (adjust according to your setup)
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Create the database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the FastAPI app
app = FastAPI()

# Create a base class for the models
Base = declarative_base()


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize the scheduler for daily task
scheduler = BackgroundScheduler()


# Define the task that checks users and sends the payment request
async def check_and_notify_users():
    # Create a session
    db = SessionLocal()
    today = datetime.today().date()

    # Query subscriptions that need to pay today
    subscriptions = (
        db.query(Subscription).filter(Subscription.next_payment_date == today).all()
    )

    # Loop through each subscription and send the GET request
    async with httpx.AsyncClient() as client:
        for sub in subscriptions:
            user = sub.user  # Access the user information
            payment_url = f"https://dummy-payment-endpoint.com/pay?user_id={user.id}&amount={sub.price}"
            try:
                response = await client.get(payment_url)
                if response.status_code == 200:
                    print(f"Payment successful for user {user.username}")
                else:
                    print(
                        f"Payment failed for user {user.username}, status code: {response.status_code}"
                    )
            except httpx.HTTPStatusError as e:
                print(f"Error for user {user.username}: {str(e)}")
            except Exception as e:
                print(f"Unexpected error for user {user.username}: {str(e)}")

    db.close()


# Add the task to the scheduler, running every day
scheduler.add_job(
    check_and_notify_users,
    IntervalTrigger(hours=24, start_date=datetime.today()),
    id="check_payment",
    name="Check users for payment every day",
)
scheduler.start()

# Create the database tables if they don't exist
Base.metadata.create_all(bind=engine)


@app.post("/subscriptions/")
def create_subscription(
    user_id: int,
    plan: str,
    next_payment_date: datetime,
    price: float,
    db: Session = Depends(get_db),
):
    db_subscription = Subscription(
        user_id=user_id,
        plan=plan,
        next_payment_date=next_payment_date.date(),
        price=price,
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)

    return db_subscription
