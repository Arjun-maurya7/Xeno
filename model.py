from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    phone = Column(String(10))
    city = Column(String(25))

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    communication_logs = relationship("CommunicationLog", back_populates="customer", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float)
    order_date = Column(Date)
    
    customer = relationship("Customer", back_populates="orders")
    campaign = relationship("Campaign", back_populates="orders")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    audience = Column(String(100))
    channel = Column(String(50))
    message = Column(String(500))
    # Status: draft | sending | completed
    status = Column(String(20), default="draft")
    # These start at 0 and are incremented by real webhook callbacks
    sent = Column(Integer, default=0)
    delivered = Column(Integer, default=0)
    opened = Column(Integer, default=0)
    clicked = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)

    orders = relationship("Order", back_populates="campaign")
    communication_logs = relationship("CommunicationLog", back_populates="campaign", cascade="all, delete-orphan")


class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"))
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    status = Column(String(20), default="sending")  # sending | sent | delivered | opened | clicked | failed | converted
    sent_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="communication_logs")
    customer = relationship("Customer", back_populates="communication_logs")
