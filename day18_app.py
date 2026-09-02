import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import sqlite3

# 1. تحميل متغيرات البيئة من ملف .env
load_dotenv()

APP_PORT = int(os.getenv("PORT", 8000))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app = FastAPI(
    title="Smart Agent API",
    description="FastAPI Backend for Smart Agent & WhatsApp Integration",
    version="2.0"
)

# نموذج للتحقق من البيانات المدخلة (Pydantic Model)
class CustomerRequest(BaseModel):
    name: str
    phone: str

# دالة مساعدة للاتصال بقاعدة البيانات SQLite
def get_db():
    conn = sqlite3.connect("agent.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# 2. المسارات (Endpoints)
@app.get("/")
async def root():
    return {
        "status": "online",
        "framework": "FastAPI",
        "message": "Smart Agent Backend is Running"
    }

@app.get("/customers")
async def list_customers(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT)")
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    return [{"id": row["id"], "name": row["name"], "phone": row["phone"]} for row in rows]

@app.post("/customers")
async def add_customer(customer: CustomerRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (customer.name, customer.phone))
    db.commit()
    return {"message": "Customer added successfully", "data": customer}

# تشغيل الخادم
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day18_app:app", host="0.0.0.0", port=APP_PORT, reload=True)

