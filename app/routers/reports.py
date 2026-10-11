

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional

from app.database import get_db
from app.utils import month_range
from app import models

router = APIRouter(prefix="/reports", tags=["Reports"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/daily")
def daily_report(request: Request, report_date: Optional[str] = None, db: Session = Depends(get_db)):
    """Ek din ki sales aur purchase bills dikhata hai."""
    selected_date = (
        datetime.strptime(report_date, "%Y-%m-%d").date() if report_date else date.today()
    )

    sales = (
        db.query(models.SaleBill)
        .filter(models.SaleBill.bill_date == selected_date)
        .all()
    )
    purchases = (
        db.query(models.PurchaseBill)
        .filter(models.PurchaseBill.bill_date == selected_date)
        .all()
    )

    total_sales = sum(s.total_amount for s in sales)
    total_purchases = sum(p.total_amount for p in purchases)

    return templates.TemplateResponse(
        "reports/daily.html",
        {
            "request": request,
            "selected_date": selected_date.isoformat(),
            "sales": sales,
            "purchases": purchases,
            "total_sales": total_sales,
            "total_purchases": total_purchases,
        },
    )


@router.get("/monthly")
def monthly_report(request: Request, month: Optional[str] = None, db: Session = Depends(get_db)):
    
    selected_month = month or date.today().strftime("%Y-%m")
    month_start, month_end = month_range(selected_month)

    sales = (
        db.query(models.SaleBill)
        .filter(models.SaleBill.bill_date >= month_start, models.SaleBill.bill_date < month_end)
        .order_by(models.SaleBill.bill_date)
        .all()
    )
    purchases = (
        db.query(models.PurchaseBill)
        .filter(models.PurchaseBill.bill_date >= month_start, models.PurchaseBill.bill_date < month_end)
        .order_by(models.PurchaseBill.bill_date)
        .all()
    )

    total_sales = sum(s.total_amount for s in sales)
    total_purchases = sum(p.total_amount for p in purchases)

    return templates.TemplateResponse(
        "reports/monthly.html",
        {
            "request": request,
            "selected_month": selected_month,
            "sales": sales,
            "purchases": purchases,
            "total_sales": total_sales,
            "total_purchases": total_purchases,
        },
    )
