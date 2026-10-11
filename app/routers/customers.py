

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models

router = APIRouter(prefix="/customers", tags=["Customers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_customers(request: Request, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).order_by(models.Customer.name).all()
    return templates.TemplateResponse(
        "customers/list.html", {"request": request, "customers": customers}
    )


@router.get("/add")
def add_customer_form(request: Request):
    return templates.TemplateResponse(
        "customers/form.html", {"request": request, "customer": None}
    )


@router.post("/add")
def add_customer(
    name: str = Form(...),
    contact: Optional[str] = Form(""),
    address: Optional[str] = Form(""),
    db: Session = Depends(get_db),
):
    customer = models.Customer(name=name, contact=contact, address=address)
    db.add(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=303)


@router.get("/edit/{customer_id}")
def edit_customer_form(customer_id: int, request: Request, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    return templates.TemplateResponse(
        "customers/form.html", {"request": request, "customer": customer}
    )


@router.post("/edit/{customer_id}")
def edit_customer(
    customer_id: int,
    name: str = Form(...),
    contact: Optional[str] = Form(""),
    address: Optional[str] = Form(""),
    db: Session = Depends(get_db),
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer:
        customer.name = name
        customer.contact = contact
        customer.address = address
        db.commit()
    return RedirectResponse(url="/customers", status_code=303)


@router.get("/delete/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
    return RedirectResponse(url="/customers", status_code=303)
