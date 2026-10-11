
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List

from app.database import get_db
from app.utils import next_bill_no
from app import models

router = APIRouter(prefix="/sales", tags=["Sales"])
templates = Jinja2Templates(directory="app/templates")


def generate_bill_no(db: Session) -> str:
    return next_bill_no(db, models.SaleBill, "SB")


@router.get("")
def list_sales(request: Request, db: Session = Depends(get_db)):
    bills = db.query(models.SaleBill).order_by(models.SaleBill.id.desc()).all()
    return templates.TemplateResponse(
        "sales/list.html", {"request": request, "bills": bills}
    )


@router.get("/add")
def add_sale_form(request: Request, error: str = "", db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    medicines = db.query(models.Medicine).all()
    return templates.TemplateResponse(
        "sales/form.html",
        {
            "request": request,
            "customers": customers,
            "medicines": medicines,
            "today": date.today().isoformat(),
            "error": error,
        },
    )


@router.post("/add")
def add_sale(
    customer_id: int = Form(...),
    bill_date: str = Form(...),
    medicine_id: List[int] = Form(...),
    quantity: List[int] = Form(...),
    unit_price: List[float] = Form(...),
    db: Session = Depends(get_db),
):
   
    # Pehle stock check: zyada bechne par bill save nahi hoga
    wanted = {}
    for med_id, qty in zip(medicine_id, quantity):
        if qty > 0:
            wanted[med_id] = wanted.get(med_id, 0) + qty
    for med_id, qty in wanted.items():
        med = db.query(models.Medicine).filter(models.Medicine.id == med_id).first()
        if not med or med.stock_quantity < qty:
            name = med.name if med else f"id {med_id}"
            have = med.stock_quantity if med else 0
            return RedirectResponse(
                url=f"/sales/add?error=Stock kam hai: {name} (maujood {have}, mangwaya {qty})",
                status_code=303,
            )

    bill = models.SaleBill(
        bill_no=generate_bill_no(db),
        customer_id=customer_id,
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

        item = models.SaleItem(
            bill_id=bill.id,
            medicine_id=med_id,
            quantity=qty,
            unit_price=price,
            total_price=line_total,
        )
        db.add(item)

        # Stock kam karna (agar available ho)
        medicine = db.query(models.Medicine).filter(models.Medicine.id == med_id).first()
        if medicine:
            medicine.stock_quantity -= qty

    bill.total_amount = total
    db.commit()
    return RedirectResponse(url="/sales", status_code=303)


@router.get("/view/{bill_id}")
def view_sale(bill_id: int, request: Request, db: Session = Depends(get_db)):
    bill = db.query(models.SaleBill).filter(models.SaleBill.id == bill_id).first()
    return templates.TemplateResponse(
        "sales/view.html", {"request": request, "bill": bill}
    )


@router.get("/delete/{bill_id}")
def delete_sale(bill_id: int, db: Session = Depends(get_db)):
   
    bill = db.query(models.SaleBill).filter(models.SaleBill.id == bill_id).first()
    if bill:
        for item in bill.items:
            medicine = db.query(models.Medicine).filter(
                models.Medicine.id == item.medicine_id
            ).first()
            if medicine:
                medicine.stock_quantity += item.quantity
        db.delete(bill)
        db.commit()
    return RedirectResponse(url="/sales", status_code=303)
