import os
from fastapi import FastAPI, Request, Response, Query
from dotenv import load_dotenv
from day20_agent_tools import run_agent

load_dotenv()

app = FastAPI(title="WhatsApp Webhook Gateway")

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
async def receive_whatsapp_message(request: Request):
    data = await request.json()
    print("\n📩 New Incoming WhatsApp Message:")
    print(data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            sender_phone = msg.get("from")
            text_body = msg.get("text", {}).get("body", "")

            print(f"📱 Sender: {sender_phone}")
            print(f"💬 Message: {text_body}")

            agent_result = run_agent(text_body, phone=sender_phone)
            print(f"🤖 Agent Response: {agent_result['agent_response']}")

            return {"status": "processed", "reply": agent_result['agent_response']}

    except Exception as e:
        print(f"⚠️ Error parsing message: {e}")

    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day21_whatsapp_webhook:app", host="0.0.0.0", port=8000, reload=True)

