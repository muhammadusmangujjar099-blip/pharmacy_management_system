

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import Base, engine, get_db
from app.utils import month_range
from app import models
from app.routers import medicines, suppliers, customers, purchases, sales, reports, chatbot

# Database ke sare tables create kar dena (agar pehle se na hon)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pharmacy Management System")

# Static files (CSS) aur templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Har router ko app mein register karna
app.include_router(medicines.router)
app.include_router(suppliers.router)
app.include_router(customers.router)
app.include_router(purchases.router)
app.include_router(sales.router)
app.include_router(reports.router)
app.include_router(chatbot.router)


@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    
    today = date.today()
    month_start, month_end = month_range(today.strftime("%Y-%m"))

    total_medicines = db.query(models.Medicine).count()
    total_suppliers = db.query(models.Supplier).count()
    total_customers = db.query(models.Customer).count()

    low_stock_medicines = (
        db.query(models.Medicine).filter(models.Medicine.stock_quantity <= 10).all()
    )

    today_sales_total = (
        db.query(func.coalesce(func.sum(models.SaleBill.total_amount), 0.0))
        .filter(models.SaleBill.bill_date == today)
        .scalar()
    )

    today_purchase_total = (
        db.query(func.coalesce(func.sum(models.PurchaseBill.total_amount), 0.0))
        .filter(models.PurchaseBill.bill_date == today)
        .scalar()
    )

    month_sales_total = (
        db.query(func.coalesce(func.sum(models.SaleBill.total_amount), 0.0))
        .filter(
            models.SaleBill.bill_date >= month_start,
            models.SaleBill.bill_date < month_end,
        )
        .scalar()
    )

    month_purchase_total = (
        db.query(func.coalesce(func.sum(models.PurchaseBill.total_amount), 0.0))
        .filter(
            models.PurchaseBill.bill_date >= month_start,
            models.PurchaseBill.bill_date < month_end,
        )
        .scalar()
    )

    recent_sales = (
        db.query(models.SaleBill).order_by(models.SaleBill.id.desc()).limit(5).all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_medicines": total_medicines,
            "total_suppliers": total_suppliers,
            "total_customers": total_customers,
            "low_stock_medicines": low_stock_medicines,
            "today_sales_total": today_sales_total,
            "today_purchase_total": today_purchase_total,
            "month_sales_total": month_sales_total,
            "month_purchase_total": month_purchase_total,
            "recent_sales": recent_sales,
            "today": today,
        },
    )
