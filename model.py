from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    phone = Column(String(10))
    city = Column(String(25))

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer, 
        ForeignKey("customers.id", ondelete="CASCADE")
    )

    amount = Column(Float)
    order_date = Column(Date)
    customer = relationship("Customer", back_populates="orders")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    audience = Column(String(100))
    channel = Column(String(50))
    message = Column(String(500))
    sent = Column(Integer, default=120)
    delivered = Column(Integer, default=110)
    opened = Column(Integer, default=85)
    clicked = Column(Integer, default=38)
