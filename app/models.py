

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime, date

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    contact = Column(String(50))
    address = Column(String(250))

    purchase_bills = relationship("PurchaseBill", back_populates="supplier")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    contact = Column(String(50))
    address = Column(String(250))

    sale_bills = relationship("SaleBill", back_populates="customer")


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), default="General")
    stock_quantity = Column(Integer, default=0)          # current stock
    purchase_price = Column(Float, default=0.0)          # cost price / unit
    sale_price = Column(Float, default=0.0)               # selling price / unit
    expiry_date = Column(Date, nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    supplier = relationship("Supplier")


class PurchaseBill(Base):
    __tablename__ = "purchase_bills"

    id = Column(Integer, primary_key=True, index=True)
    bill_no = Column(String(50), unique=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    bill_date = Column(Date, default=date.today)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="purchase_bills")
    items = relationship(
        "PurchaseItem", back_populates="bill", cascade="all, delete-orphan"
    )


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("purchase_bills.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)

    bill = relationship("PurchaseBill", back_populates="items")
    medicine = relationship("Medicine")


class SaleBill(Base):
    __tablename__ = "sale_bills"

    id = Column(Integer, primary_key=True, index=True)
    bill_no = Column(String(50), unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    bill_date = Column(Date, default=date.today)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="sale_bills")
    items = relationship(
        "SaleItem", back_populates="bill", cascade="all, delete-orphan"
    )


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("sale_bills.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)

    bill = relationship("SaleBill", back_populates="items")
    medicine = relationship("Medicine")
