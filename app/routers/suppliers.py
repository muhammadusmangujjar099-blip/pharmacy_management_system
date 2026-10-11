

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_suppliers(request: Request, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).order_by(models.Supplier.name).all()
    return templates.TemplateResponse(
        "suppliers/list.html", {"request": request, "suppliers": suppliers}
    )


@router.get("/add")
def add_supplier_form(request: Request):
    return templates.TemplateResponse(
        "suppliers/form.html", {"request": request, "supplier": None}
    )


@router.post("/add")
def add_supplier(
    name: str = Form(...),
    contact: Optional[str] = Form(""),
    address: Optional[str] = Form(""),
    db: Session = Depends(get_db),
):
    supplier = models.Supplier(name=name, contact=contact, address=address)
    db.add(supplier)
    db.commit()
    return RedirectResponse(url="/suppliers", status_code=303)


@router.get("/edit/{supplier_id}")
def edit_supplier_form(supplier_id: int, request: Request, db: Session = Depends(get_db)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    return templates.TemplateResponse(
        "suppliers/form.html", {"request": request, "supplier": supplier}
    )


@router.post("/edit/{supplier_id}")
def edit_supplier(
    supplier_id: int,
    name: str = Form(...),
    contact: Optional[str] = Form(""),
    address: Optional[str] = Form(""),
    db: Session = Depends(get_db),
):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if supplier:
        supplier.name = name
        supplier.contact = contact
        supplier.address = address
        db.commit()
    return RedirectResponse(url="/suppliers", status_code=303)


@router.get("/delete/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if supplier:
        db.delete(supplier)
        db.commit()
    return RedirectResponse(url="/suppliers", status_code=303)
