import math
import re

# In-memory storage for agent knowledge
memory_db = []

def tokenize(text: str) -> set:
    """Extract unique lowercase words from text."""
    words = re.findall(r'\w+', text.lower())
    return set(words)

def store_knowledge(doc_id: str, text: str, category: str):
    """Store knowledge items with tokenized representations."""
    words = tokenize(text)
    memory_db.append({
        "id": doc_id,
        "text": text,
        "category": category,
        "tokens": words
    })
    print(f"✅ Knowledge stored successfully: [{doc_id}]")

def search_knowledge(query: str) -> str:
    """Search for the most relevant document using Jaccard Similarity."""
    if not memory_db:
        return "Memory is empty."
    
    query_tokens = tokenize(query)
    best_match = None
    highest_score = -1.0

    for item in memory_db:
        intersection = query_tokens.intersection(item["tokens"])
        union = query_tokens.union(item["tokens"])
        
        # Calculate similarity score
        score = len(intersection) / len(union) if union else 0.0
        
        if score > highest_score:
            highest_score = score
            best_match = item["text"]

    return best_match if highest_score > 0 else "No relevant information found."

if __name__ == "__main__":
    print("--- Initializing Agent Memory ---")
    
    # Adding sample knowledge base
    store_knowledge(
        "info_1", 
        "Official business hours are Sunday through Thursday from 9 AM to 5 PM.", 
        "working_hours"
    )
    store_knowledge(
        "info_2", 
        "Our return policy allows items to be returned within 14 days of purchase.", 
        "policies"
    )
    store_knowledge(
        "info_3", 
        "The headquarters is located in Riyadh at Al Malqa district.", 
        "location"
    )

    print("\n--- Testing Lightweight RAG Search ---")
    
    query = "What are the business hours and opening times?"
    retrieved_info = search_knowledge(query)
    
    print(f"Query: {query}")
    print(f"Retrieved Knowledge: {retrieved_info}")

