# Pharmacy Management System (FastAPI + SQLite)

## Features
- Dashboard (aaj / is mahine ki sale & purchase, low stock alert)
- Medicines (stock, purchase/sale price, expiry, supplier) + search
- Suppliers aur Customers (naam, contact, address)
- Purchase Bills (multiple items, stock automatically barhta hai)
- Sale Bills (multiple items, stock automatically kam hota hai)
- Daily Report aur Monthly Report
- Bills print karne ka option

## Run karne ka tarika
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Browser mein kholein: http://127.0.0.1:8000

Database file `pharmacy.db` pehli dafa run par khud ban jati hai.
(Demo data chahiye to: `python seed_data.py`)

## Folder Structure
```
pharmacy_management_system/
├── app/
│   ├── main.py          # FastAPI app + dashboard
│   ├── database.py      # SQL connection
│   ├── models.py        # Database tables
│   ├── routers/         # medicines, suppliers, customers, purchases, sales, reports
│   ├── templates/       # HTML pages (Jinja2 + Bootstrap)
│   └── static/css/      # Styling
├── seed_data.py         # Demo data
├── requirements.txt
└── README.md
```
## Database aur Chatbot
- Default database **SQLite** hai (`pharmacy.db`), koi server install nahi karna.
- PostgreSQL/MySQL chahiye to `.env` file mein `DATABASE_URL` set karein (`.env.example` dekhein).
- Chatbot ke liye `.env` mein `OPENROUTER_API_KEY` dalein. Key na ho to baqi app normal chalti hai.

## Is version mein kya theek kiya gaya
- `database.py` mein Postgres ka hardcoded URL tha, to server na hone par app start hi nahi hoti thi. Ab default SQLite hai.
- `requirements.txt` mein `python-dotenv` aur `requests` missing the.
- Dashboard/Reports mein `to_char` (sirf Postgres) aur chatbot mein `strftime` (sirf SQLite) tha. Ab sab jagah ek hi tarika chalta hai jo dono par kaam karta hai.
- Stock se zyada sale karne par stock chupke se 0 ho jata tha. Ab bill save nahi hota aur error dikhta hai.
- Bill delete karne ke baad naya bill number duplicate ho sakta tha. Ab hamesha unique number banta hai.
