
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional

from app.database import get_db
from app.utils import next_bill_no
from app import models

router = APIRouter(prefix="/purchases", tags=["Purchases"])
templates = Jinja2Templates(directory="app/templates")


def generate_bill_no(db: Session) -> str:
    return next_bill_no(db, models.PurchaseBill, "PB")


@router.get("")
def list_purchases(request: Request, db: Session = Depends(get_db)):
    bills = db.query(models.PurchaseBill).order_by(models.PurchaseBill.id.desc()).all()
    return templates.TemplateResponse(
        "purchases/list.html", {"request": request, "bills": bills}
    )


@router.get("/add")
def add_purchase_form(request: Request, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).all()
    medicines = db.query(models.Medicine).all()
    return templates.TemplateResponse(
        "purchases/form.html",
        {
            "request": request,
            "suppliers": suppliers,
            "medicines": medicines,
            "today": date.today().isoformat(),
        },
    )


@router.post("/add")
def add_purchase(
    supplier_id: int = Form(...),
    bill_date: str = Form(...),
    medicine_id: List[int] = Form(...),
    quantity: List[int] = Form(...),
    unit_price: List[float] = Form(...),
    db: Session = Depends(get_db),
):
   
    bill = models.PurchaseBill(
        bill_no=generate_bill_no(db),
        supplier_id=supplier_id,
        bill_date=datetime.strptime(bill_date, "%Y-%m-%d").date(),
        total_amount=0.0,
    )
    db.add(bill)
    db.flush()  
    total = 0.0
    for med_id, qty, price in zip(medicine_id, quantity, unit_price):
        if qty <= 0:
            continue
        line_total = qty * price
        total += line_total

        item = models.PurchaseItem(
            bill_id=bill.id,
            medicine_id=med_id,
            quantity=qty,
            unit_price=price,
            total_price=line_total,
        )
        db.add(item)

        # Stock badhana + purchase price update karna
        medicine = db.query(models.Medicine).filter(models.Medicine.id == med_id).first()
        if medicine:
            medicine.stock_quantity += qty
            medicine.purchase_price = price

    bill.total_amount = total
    db.commit()
    return RedirectResponse(url="/purchases", status_code=303)


@router.get("/view/{bill_id}")
def view_purchase(bill_id: int, request: Request, db: Session = Depends(get_db)):
    bill = db.query(models.PurchaseBill).filter(models.PurchaseBill.id == bill_id).first()
    return templates.TemplateResponse(
        "purchases/view.html", {"request": request, "bill": bill}
    )


@router.get("/delete/{bill_id}")
def delete_purchase(bill_id: int, db: Session = Depends(get_db)):
    
    bill = db.query(models.PurchaseBill).filter(models.PurchaseBill.id == bill_id).first()
    if bill:
        for item in bill.items:
            medicine = db.query(models.Medicine).filter(
                models.Medicine.id == item.medicine_id
            ).first()
            if medicine:
                medicine.stock_quantity = max(0, medicine.stock_quantity - item.quantity)
        db.delete(bill)
        db.commit()
    return RedirectResponse(url="/purchases", status_code=303)
