"""Chhote helper functions (SQLite aur PostgreSQL dono par chalte hain)."""
from datetime import date
from typing import Tuple

from sqlalchemy.orm import Session


def month_range(month: str) -> Tuple[date, date]:
    """'2026-09' -> (2026-09-01, 2026-10-01). Filter: start <= date < end."""
    year, mon = map(int, month.split("-"))
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return start, end


def next_bill_no(db: Session, model, prefix: str) -> str:
    """
    Naya unique bill number (SB-0001 / PB-0001).
    Purani galti: count()+1 use hota tha, bill delete hone par number duplicate
    ho kar app crash kar deta tha. Ab sab se bara id use hota hai.
    """
    last_id = db.query(model.id).order_by(model.id.desc()).limit(1).scalar() or 0
    number = last_id + 1
    while db.query(model.id).filter(model.bill_no == f"{prefix}-{number:04d}").first():
        number += 1
    return f"{prefix}-{number:04d}"
