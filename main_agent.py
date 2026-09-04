import os
import sqlite3
import requests
from fastapi import FastAPI, Request, Response, Query, BackgroundTasks, status
from dotenv import load_dotenv
from day20_agent_tools import run_agent

load_dotenv()

app = FastAPI(title="Smart Agent V2 - Production Unified System", version="2.0.0")

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_token_123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "mock_access_token")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "mock_phone_id")

# --- Database & Session Memory ---
def init_db():
    conn = sqlite3.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenant_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            role TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_chat_history(phone: str, role: str, message: str):
    conn = sqlite3.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tenant_sessions (phone, role, message) VALUES (?, ?, ?)", (phone, role, message))
    conn.commit()
    conn.close()

# --- Outbound Messaging Handler ---
def send_whatsapp_message(to_phone: str, message_text: str) -> dict:
    if WHATSAPP_TOKEN == "mock_access_token":
        print(f"📡 [MOCK OUTBOUND] Sent to {to_phone}: {message_text}")
        return {"status": "mock_sent", "to": to_phone, "message": message_text}

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to_phone, "type": "text", "text": {"body": message_text}}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return {"status_code": response.status_code, "data": response.json()}
    except Exception as e:
        return {"status": "error", "details": str(e)}

# --- Background Processing Worker ---
def async_agent_worker(sender_phone: str, text_body: str):
    save_chat_history(sender_phone, "user", text_body)
    agent_output = run_agent(text_body, phone=sender_phone)
    reply_text = agent_output["agent_response"]
    save_chat_history(sender_phone, "agent", reply_text)
    
    send_whatsapp_message(sender_phone, reply_text)
    print(f"✅ [Worker Done] Replied to {sender_phone}: {reply_text}")

# --- API Endpoints ---
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
async def health_check(response: Response):
    try:
        conn = sqlite3.connect("agent.db")
        conn.cursor().execute("SELECT 1;")
        conn.close()
        return {"status": "healthy", "database": "connected", "environment": "Termux (Android Native)"}
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "database": "disconnected"}

@app.get("/webhook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            sender_phone = msg.get("from")
            text_body = msg.get("text", {}).get("body", "")

            background_tasks.add_task(async_agent_worker, sender_phone, text_body)
            return {"status": "accepted"}
    except Exception as e:
        print(f"⚠️ Webhook error: {e}")

    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_agent:app", host="0.0.0.0", port=8000, reload=True)

