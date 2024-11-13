from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from enum import Enum as PyEnum
from datetime import datetime


# Define the Enum class for Subscription Plan
class PlanType(PyEnum):
    BASIC = "BASIC"
    PRO = "PRO"
    ULTIMATE = "ULTIMATE"


# Create a base class for the models
Base = declarative_base()


# Define the User and Subscription models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan = Column(Enum(PlanType), nullable=False)  # Use Enum for the 'plan' column
    next_payment_date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)

    user = relationship("User", back_populates="subscriptions")


# Add the relationship on the User model
User.subscriptions = relationship("Subscription", back_populates="user")

# Database setup (adjust the database URL)
DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)

# Create tables in the database
Base.metadata.create_all(bind=engine)
