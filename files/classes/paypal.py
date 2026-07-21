from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from files.classes import Base


class PaypalSubscription(Base):
    __tablename__ = "paypal_subscriptions"

    subscription_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String, nullable=False)
    tier = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    payer_email = Column(String)
    created_utc = Column(Integer, nullable=False)
    updated_utc = Column(Integer, nullable=False)
    next_billing_utc = Column(Integer)
    last_payment_utc = Column(Integer)
    cancelled_utc = Column(Integer)


class PaypalPayment(Base):
    __tablename__ = "paypal_payments"

    payment_id = Column(String, primary_key=True)
    subscription_id = Column(String, ForeignKey("paypal_subscriptions.subscription_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tier = Column(Integer, nullable=False)
    gross_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False)
    wishbux_granted = Column(Integer, nullable=False, default=0)
    created_utc = Column(Integer, nullable=False)
    updated_utc = Column(Integer, nullable=False)


class PaypalWebhookEvent(Base):
    __tablename__ = "paypal_webhook_events"

    event_id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)
    resource_id = Column(String)
    received_utc = Column(Integer, nullable=False)
    processed = Column(Boolean, nullable=False, default=False)
