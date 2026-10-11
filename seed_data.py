"""Demo data insert karne ke liye: python seed_data.py"""
from datetime import date, timedelta
from app.database import Base, engine, SessionLocal
from app import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

s1 = models.Supplier(name="Al-Shifa Distributors", contact="0300-1234567", address="Lahore")
s2 = models.Supplier(name="Medico Traders", contact="0321-7654321", address="Karachi")
c1 = models.Customer(name="Ali Khan", contact="0333-1111111", address="Lahore")
c2 = models.Customer(name="Sara Ahmed", contact="0345-2222222", address="Islamabad")
db.add_all([s1, s2, c1, c2]); db.flush()

meds = [
    ("Panadol 500mg", "Painkiller", 120, 8, 12, s1.id),
    ("Augmentin 625mg", "Antibiotic", 60, 90, 130, s1.id),
    ("Brufen 400mg", "Painkiller", 8, 6, 10, s2.id),
    ("Disprin", "Painkiller", 200, 2, 4, s2.id),
    ("Amoxil 500mg", "Antibiotic", 5, 45, 70, s1.id),
]
for n, cat, stock, pp, sp, sid in meds:
    db.add(models.Medicine(name=n, category=cat, stock_quantity=stock, purchase_price=pp,
                           sale_price=sp, supplier_id=sid, expiry_date=date.today() + timedelta(days=365)))
db.commit(); db.close()
print("Demo data added.")
