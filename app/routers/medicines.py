

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app import models

router = APIRouter(prefix="/medicines", tags=["Medicines"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_medicines(request: Request, q: Optional[str] = None, db: Session = Depends(get_db)):
    """Sari medicines ki list, optional search (naam se) ke sath."""
    query = db.query(models.Medicine)
    if q:
        query = query.filter(models.Medicine.name.ilike(f"%{q}%"))
    medicines = query.order_by(models.Medicine.name).all()
    return templates.TemplateResponse(
        "medicines/list.html", {"request": request, "medicines": medicines, "q": q or ""}
    )


@router.get("/add")
def add_medicine_form(request: Request, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).all()
    return templates.TemplateResponse(
        "medicines/form.html",
        {"request": request, "medicine": None, "suppliers": suppliers},
    )


@router.post("/add")
def add_medicine(
    name: str = Form(...),
    category: str = Form("General"),
    stock_quantity: int = Form(0),
    purchase_price: float = Form(0.0),
    sale_price: float = Form(0.0),
    expiry_date: Optional[str] = Form(None),
    supplier_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Nayi medicine database mein add karta hai."""
    exp = None
    if expiry_date:
        exp = datetime.strptime(expiry_date, "%Y-%m-%d").date()

    medicine = models.Medicine(
        name=name,
        category=category,
        stock_quantity=stock_quantity,
        purchase_price=purchase_price,
        sale_price=sale_price,
        expiry_date=exp,
        supplier_id=int(supplier_id) if supplier_id else None,
    )
    db.add(medicine)
    db.commit()
    return RedirectResponse(url="/medicines", status_code=303)


@router.get("/edit/{medicine_id}")
def edit_medicine_form(medicine_id: int, request: Request, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    suppliers = db.query(models.Supplier).all()
    return templates.TemplateResponse(
        "medicines/form.html",
        {"request": request, "medicine": medicine, "suppliers": suppliers},
    )


@router.post("/edit/{medicine_id}")
def edit_medicine(
    medicine_id: int,
    name: str = Form(...),
    category: str = Form("General"),
    stock_quantity: int = Form(0),
    purchase_price: float = Form(0.0),
    sale_price: float = Form(0.0),
    expiry_date: Optional[str] = Form(None),
    supplier_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Existing medicine ki details update karta hai."""
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if medicine:
        medicine.name = name
        medicine.category = category
        medicine.stock_quantity = stock_quantity
        medicine.purchase_price = purchase_price
        medicine.sale_price = sale_price
        medicine.expiry_date = (
            datetime.strptime(expiry_date, "%Y-%m-%d").date() if expiry_date else None
        )
        medicine.supplier_id = int(supplier_id) if supplier_id else None
        db.commit()
    return RedirectResponse(url="/medicines", status_code=303)


@router.get("/delete/{medicine_id}")
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if medicine:
        db.delete(medicine)
        db.commit()
    return RedirectResponse(url="/medicines", status_code=303)
