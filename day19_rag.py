import math
import re

# قاعدة بيانات خفيفة في الذاكرة
memory_db = []

def tokenize(text):
    # تفكيك النص إلى كلمات وتطنيش العلامات
    words = re.findall(r'\w+', text.lower())
    return set(words)

def store_knowledge(doc_id: str, text: str, category: str):
    words = tokenize(text)
    memory_db.append({
        "id": doc_id,
        "text": text,
        "category": category,
        "tokens": words
    })
    print(f"✅ تم حفظ المعلومة: {doc_id}")

def search_knowledge(query: str):
    if not memory_db:
        return "الذاكرة فارغة"
    
    query_tokens = tokenize(query)
    best_match = None
    highest_score = -1

    for item in memory_db:
        # حساب نسبة التشابه بين الكلمات (Jaccard Similarity)
        intersection = query_tokens.intersection(item["tokens"])
        union = query_tokens.union(item["tokens"])
        
        score = len(intersection) / len(union) if union else 0
        
        if score > highest_score:
            highest_score = score
            best_match = item["text"]

    return best_match

if __name__ == "__main__":
    # إضافة البيانات التجريبية
    store_knowledge("info_1", "ساعات العمل الرسمية من الأحد إلى الخميس من 9 صباحاً حتى 5 مساءً", "working_hours")
    store_knowledge("info_2", "سياسة الاسترجاع تسمح بإعادة المنتج خلال 14 يوم من الشراء", "policies")
    store_knowledge("info_3", "موقع الشركة الرئيسي في مدينة الرياض حي الملقا", "location")

    print("\n--- تجربة البحث في الذاكرة (Lightweight RAG) ---")
    query = "ما هي ساعات العمل والتوقيت؟"
    matched_info = search_knowledge(query)
    
    print(f"السؤال: {query}")
    print(f"المعلومة المسترجعة: {matched_info}")

