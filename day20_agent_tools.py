import json
import sqlite3
from day19_rag import store_knowledge, search_knowledge

# 1. Initialize Sample Data
store_knowledge("hours", "Business hours: Sun-Thu from 9 AM to 5 PM", "info")
store_knowledge("policy", "Returns are allowed within 14 days", "info")

# 2. Define Tools
def get_customer_orders(phone_number: str) -> str:
    """Tool 1: Query database for customer orders by phone number."""
    conn = sqlite3.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (phone TEXT, item TEXT)")
    cursor.execute("SELECT item FROM orders WHERE phone=?", (phone_number,))
    results = cursor.fetchall()
    conn.close()
    
    if results:
        items = ", ".join([row[0] for row in results])
        return f"Orders for {phone_number}: {items}"
    return f"No active orders found for {phone_number}"

def query_knowledge_base(query: str) -> str:
    """Tool 2: Query the memory/RAG system for general information."""
    return search_knowledge(query)

# 3. Smart Router (Agent Brain)
def run_agent(user_prompt: str, phone: str = None) -> dict:
    """
    Decides which tool to invoke based on user intent.
    """
    user_prompt_lower = user_prompt.lower()
    
    # Tool Selection Logic
    if any(keyword in user_prompt_lower for keyword in ["order", "status", "buy", "purchase"]):
        tool_used = "database_tool"
        output = get_customer_orders(phone if phone else "unknown")
    else:
        tool_used = "rag_knowledge_tool"
        output = query_knowledge_base(user_prompt)

    return {
        "user_query": user_prompt,
        "selected_tool": tool_used,
        "agent_response": output
    }

if __name__ == "__main__":
    print("--- Testing Agent Tool Calling Logic ---\n")
    
    # Test Scenario 1: General Info Query (Triggers RAG Tool)
    q1 = "What time do you close?"
    res1 = run_agent(q1)
    print(json.dumps(res1, indent=2))
    
    print("\n" + "="*40 + "\n")
    
    # Test Scenario 2: Order Query (Triggers Database Tool)
    q2 = "Check my order status"
    res2 = run_agent(q2, phone="123456789")
    print(json.dumps(res2, indent=2))

