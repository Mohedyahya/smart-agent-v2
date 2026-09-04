import os
from fastapi import FastAPI, Request, Response, Query
from dotenv import load_dotenv
from day22_multitenant import process_tenant_message, init_tenant_db
from day24_whatsapp_outbound import send_whatsapp_message

load_dotenv()
init_tenant_db()

app = FastAPI(title="Day 25: Full End-to-End WhatsApp Agent")

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_token_123")

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
async def receive_and_reply(request: Request):
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

            print(f"\n📩 Incoming from [{sender_phone}]: {text_body}")

            # 1. Process query & save context
            result = process_tenant_message(sender_phone, text_body)
            reply_text = result['current_response']
            
            # 2. Dispatch outbound message back to WhatsApp user
            outbound_status = send_whatsapp_message(sender_phone, reply_text)
            
            print(f"🤖 Agent Response Dispatched: {reply_text}")
            return {
                "status": "success",
                "tenant": sender_phone,
                "reply": reply_text,
                "outbound_delivery": outbound_status
            }

    except Exception as e:
        print(f"⚠️ Webhook processing error: {e}")

    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day25_end_to_end:app", host="0.0.0.0", port=8000, reload=True)

