import os
import requests
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "mock_access_token")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "mock_phone_id")

def send_whatsapp_message(to_phone: str, message_text: str) -> dict:
    """Send message via Meta WhatsApp Cloud API with Mock Fallback for local dev."""
    # If using mock token, skip real API call to avoid 401 error during development
    if WHATSAPP_TOKEN == "mock_access_token":
        print(f"📡 [MOCK OUTBOUND] Sent to {to_phone}: {message_text}")
        return {"status": "mock_sent", "to": to_phone, "message": message_text}

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message_text}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return {"status_code": response.status_code, "data": response.json()}
    except Exception as e:
        return {"status": "error", "details": str(e)}

if __name__ == "__main__":
    print("--- Testing Outbound WhatsApp Handler ---")
    res = send_whatsapp_message("966599999999", "Hello! Your agent is ready.")
    print("Execution Result:", res)

