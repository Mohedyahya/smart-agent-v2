import os
from fastapi import FastAPI, Request, Response, Query, BackgroundTasks
from dotenv import load_dotenv
from day22_multitenant import process_tenant_message, init_tenant_db
from day24_whatsapp_outbound import send_whatsapp_message

load_dotenv()
init_tenant_db()

app = FastAPI(title="Day 26: Async Background Processing Agent")

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_token_123")

def process_and_respond_task(sender_phone: str, text_body: str):
    """Background task to run agent logic and dispatch outbound reply."""
    print(f"⚡ [Async Worker Started] Processing for {sender_phone}...")
    result = process_tenant_message(sender_phone, text_body)
    reply_text = result['current_response']
    
    outbound_status = send_whatsapp_message(sender_phone, reply_text)
    print(f"✅ [Async Worker Completed] Sent reply to {sender_phone}: {reply_text}")

@app.get("/webhook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_whatsapp_async(request: Request, background_tasks: BackgroundTasks):
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

            print(f"\n📩 Incoming Webhook from [{sender_phone}]: {text_body}")

            # Offload heavy AI processing to background worker
            background_tasks.add_task(process_and_respond_task, sender_phone, text_body)
            
            # Immediate response to Meta Webhook (< 100ms)
            return {"status": "accepted", "message": "Queued for background processing"}

    except Exception as e:
        print(f"⚠️ Webhook processing error: {e}")

    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day26_async_tasks:app", host="0.0.0.0", port=8000, reload=True)

