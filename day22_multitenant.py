import sqlite3
import json
from day20_agent_tools import run_agent

def init_tenant_db():
    """Create session persistence table."""
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
    """Store message tied to a specific phone number."""
    conn = sqlite3.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tenant_sessions (phone, role, message) VALUES (?, ?, ?)", (phone, role, message))
    conn.commit()
    conn.close()

def get_chat_history(phone: str, limit: int = 5):
    """Fetch isolated chat memory for a specific tenant."""
    conn = sqlite3.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, message FROM tenant_sessions WHERE phone=? ORDER BY id DESC LIMIT ?", (phone, limit))
    rows = cursor.fetchall()
    conn.close()
    return list(reversed(rows))

def process_tenant_message(phone: str, user_message: str) -> dict:
    """Process incoming query while maintaining isolated state."""
    save_chat_history(phone, "user", user_message)
    agent_output = run_agent(user_message, phone=phone)
    response_text = agent_output["agent_response"]
    save_chat_history(phone, "agent", response_text)
    
    return {
        "tenant_phone": phone,
        "history": get_chat_history(phone),
        "current_response": response_text
    }

if __name__ == "__main__":
    init_tenant_db()
    print("--- Testing Multi-Tenant Memory Isolation ---\n")
    
    # Test Tenant A
    user1 = process_tenant_message("966500000001", "What time do you close?")
    print("📱 User 1 (Tenant A):")
    print(json.dumps(user1, indent=2))
    
    print("\n" + "="*40 + "\n")
    
    # Test Tenant B
    user2 = process_tenant_message("966500000002", "Check my order status")
    print("📱 User 2 (Tenant B):")
    print(json.dumps(user2, indent=2))

