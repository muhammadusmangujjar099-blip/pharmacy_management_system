"""
Chatbot Router (OpenRouter version)
---------------------------------------
Pharmacy database se sawal-jawab karne wala AI chatbot.
OpenRouter ko hamare database functions "tools" ke taur par dikhaye jate
hain, AI khud faisla karta hai kaun sa function chalana hai (jaise stock
dekhna, sale nikalna, waghera), phir jawab Urdu/English mein deta hai.
"""

import os
import json
import requests
from datetime import date
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.utils import month_range
from app import models

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-chat"


class ChatRequest(BaseModel):
    message: str


def get_stock(db: Session, medicine_name: str) -> str:
    medicine = (
        db.query(models.Medicine)
        .filter(models.Medicine.name.ilike(f"%{medicine_name}%"))
        .first()
    )
    if not medicine:
        return f"'{medicine_name}' naam ki koi medicine nahi mili."
    return (
        f"{medicine.name} ka stock {medicine.stock_quantity} units hai, "
        f"sale price Rs. {medicine.sale_price} hai."
    )


def get_today_sales(db: Session) -> str:
    today = date.today()
    total = (
        db.query(func.coalesce(func.sum(models.SaleBill.total_amount), 0.0))
        .filter(models.SaleBill.bill_date == today)
        .scalar()
    )
    return f"Aaj ({today}) ki total sale Rs. {total:.2f} hui hai."


def get_monthly_sales(db: Session, month: str = "") -> str:
    selected_month = month or date.today().strftime("%Y-%m")
    try:
        month_start, month_end = month_range(selected_month)
    except ValueError:
        return "Mahina YYYY-MM format mein dein, jaise 2026-09."
    total = (
        db.query(func.coalesce(func.sum(models.SaleBill.total_amount), 0.0))
        .filter(
            models.SaleBill.bill_date >= month_start,
            models.SaleBill.bill_date < month_end,
        )
        .scalar()
    )
    return f"{selected_month} ki total sale Rs. {total:.2f} hui hai."


def get_low_stock(db: Session) -> str:
    meds = db.query(models.Medicine).filter(models.Medicine.stock_quantity <= 10).all()
    if not meds:
        return "Koi bhi medicine low stock mein nahi hai."
    lines = [f"{m.name}: {m.stock_quantity} units" for m in meds]
    return "Low stock medicines:\n" + "\n".join(lines)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock",
            "description": "Kisi khaas medicine ka maujooda stock aur sale price batata hai.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medicine_name": {"type": "string", "description": "Medicine ka naam"}
                },
                "required": ["medicine_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_sales",
            "description": "Aaj ki total sale (Rs.) batata hai.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_monthly_sales",
            "description": "Kisi mahine ki total sale (Rs.) batata hai.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": "Format YYYY-MM, jaise 2026-09. Khaali chhodein to is mahine ki sale.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_low_stock",
            "description": "Jin medicines ka stock 10 ya kam hai, unki list deta hai.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def run_tool(db: Session, name: str, tool_args: dict) -> str:
    if name == "get_stock":
        return get_stock(db, tool_args.get("medicine_name", ""))
    if name == "get_today_sales":
        return get_today_sales(db)
    if name == "get_monthly_sales":
        return get_monthly_sales(db, tool_args.get("month", ""))
    if name == "get_low_stock":
        return get_low_stock(db)
    return "Yeh tool maujood nahi hai."


def call_openrouter(messages: list) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "tools": TOOLS,
        "messages": messages,
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


@router.post("/ask")
def ask_chatbot(req: ChatRequest, db: Session = Depends(get_db)):
    if not OPENROUTER_API_KEY:
        return {"reply": "API key set nahi hai. '.env' file mein OPENROUTER_API_KEY dalein."}

    messages = [{"role": "user", "content": req.message}]

    try:
        data = call_openrouter(messages)
        message = data["choices"][0]["message"]

        while message.get("tool_calls"):
            messages.append(message)

            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"] or "{}")
                result_text = run_tool(db, tool_name, tool_args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result_text,
                    }
                )

            data = call_openrouter(messages)
            message = data["choices"][0]["message"]

        return {"reply": message.get("content") or "Jawab nahi mil saka."}

    except requests.exceptions.RequestException as e:
        return {"reply": f"Error aaya: {e}"}
