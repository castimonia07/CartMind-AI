import os
import json
import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import google.generativeai as genai

# Setup Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class IntentResult(BaseModel):
    intent: str  # ADD_ITEM, REMOVE_ITEM, CLEAR_CART, SHOW_CART, RECOMMEND, FIND_SUBSTITUTE, OPTIMIZE_CART, WHAT_IF
    category: Optional[str] = None
    items: List[Dict[str, Any]] = []
    hard_constraints: Dict[str, Any] = {}
    soft_preferences: Dict[str, float] = {}
    requested_action: Optional[str] = None
    raw_text: Optional[str] = None

SYSTEM_PROMPT = """
You are the NLU parser for an AI-powered smart shopping assistant.
Your task is to parse Hinglish / English user queries into structured JSON.

Supported Intents:
- "ADD_ITEM": Adding one or multiple items/groceries to list or cart (e.g., "add 2kg rice", "1 packet bread daal do").
- "REMOVE_ITEM": Removing items (e.g., "remove oats", "chawal hatao").
- "CLEAR_CART": Emptying the basket (e.g., "clear cart", "sab delete kardo").
- "SHOW_CART": Viewing items (e.g., "kya kya hai list me", "show cart").
- "RECOMMEND": Product recommendation/decision search (e.g., "best laptop under 80k for ML", "running shoes under 3000", "suggest lightweight laptop").
- "FIND_SUBSTITUTE": Asking for alternatives (e.g., "is there any cheaper alternative", "oats ka substitute").
- "OPTIMIZE_CART": Optimizing total cost or nutritional value.
- "WHAT_IF": Budget/trade-off queries (e.g., "what if I increase budget by 10k").

Output Format: Strictly valid JSON matching this schema:
{
  "intent": "ADD_ITEM" | "REMOVE_ITEM" | "CLEAR_CART" | "SHOW_CART" | "RECOMMEND" | "FIND_SUBSTITUTE" | "OPTIMIZE_CART" | "WHAT_IF",
  "category": "Laptops" | "Smartphones" | "Electronics" | "Grocery" | "Fashion" | "Fitness" | null,
  "items": [
    {"raw_query": "rice", "quantity": 2.0, "unit": "kg"}
  ],
  "hard_constraints": {
    "max_budget": 80000.0,
    "min_ram_gb": 16,
    "max_weight_kg": 1.8,
    "requires_gpu": true,
    "dietary_restrictions": ["vegan"]
  },
  "soft_preferences": {
    "performance": 0.9,
    "battery": 0.8,
    "portability": 0.7,
    "value": 0.85
  }
}
Keep numeric budget in INR (e.g., 80k = 80000). Return ONLY the JSON object, no Markdown backticks or commentary.
"""

def _extract_budget(text: str) -> Optional[float]:
    patterns = [
        r'(?:under|below|less than|max|within|upto|up to|se kam|se zyada nahi|around|approx)\s*[₹rs]?\s*(\d+[\d,]*)\s*(k\b|lakh\b|lac\b)?',
        r'[₹rs]\s*(\d+[\d,]*)\s*(k\b|lakh\b|lac\b)?',
        r'(\d+[\d,]*)\s*(k\b|lakh\b|lac\b)?\s*(?:budget|rupees|rs|tak)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = float(m.group(1).replace(',', ''))
            suffix = (m.group(2) or '').lower()
            if suffix == 'k':
                val *= 1000
            elif suffix in ['lakh', 'lac']:
                val *= 100000
            return val
    return None

def _extract_quantity_and_product(text: str):
    qty_map = {'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'paanch': 5, 'one': 1, 'two': 2, 'three': 3, 'half': 0.5, 'aadha': 0.5}
    m = re.search(r'(\d+\.?\d*)\s*(kg|gm|gram|g|litre|liter|l|ml|piece|pcs|packet|pack|bottle|box|dozen)?\s*(?:of\s+)?(.+)', text, re.IGNORECASE)
    if m:
        qty = float(m.group(1))
        unit = m.group(2) or 'piece'
        product = m.group(3).strip()
        return qty, unit, product
    
    for word, num in qty_map.items():
        if re.search(r'\b' + word + r'\b', text, re.IGNORECASE):
            product = re.sub(r'\b' + word + r'\b', '', text, flags=re.IGNORECASE).strip()
            return float(num), 'piece', product
            
    return 1.0, 'piece', text.strip()

def _detect_category(text: str) -> Optional[str]:
    categories = {
        'laptop': 'Laptops', 'notebook': 'Laptops', 'macbook': 'Laptops',
        'phone': 'Smartphones', 'smartphone': 'Smartphones', 'mobile': 'Smartphones',
        'headphone': 'Electronics', 'earphone': 'Electronics', 'earbuds': 'Electronics', 'speaker': 'Electronics',
        'rice': 'Grocery', 'milk': 'Grocery', 'bread': 'Grocery', 'oats': 'Grocery',
        'doodh': 'Grocery', 'chawal': 'Grocery', 'atta': 'Grocery', 'oil': 'Grocery',
        'shoe': 'Fashion', 'shirt': 'Fashion', 'jacket': 'Fashion', 'sneakers': 'Fashion'
    }
    tl = text.lower()
    for kw, cat in categories.items():
        if kw in tl:
            return cat
    return None

def _extract_soft_preferences(text: str) -> Dict[str, float]:
    prefs = {}
    tl = text.lower()
    
    if any(w in tl for w in ['machine learning', 'ml', 'ai', 'data science', 'deep learning', 'coding', 'development']):
        prefs['ml_performance'] = 0.95
        prefs['performance'] = 0.90
    if any(w in tl for w in ['gaming', 'gpu', 'graphic']):
        prefs['gaming'] = 0.9
        prefs['performance'] = 0.85
    if any(w in tl for w in ['travel', 'portable', 'light', 'lightweight', 'portability', 'halka']):
        prefs['portability'] = 0.85
    if any(w in tl for w in ['battery', 'backup', 'charge', 'long lasting']):
        prefs['battery'] = 0.85
    if any(w in tl for w in ['cheap', 'budget', 'affordable', 'value', 'sasta', 'paisa vasool']):
        prefs['value'] = 0.90
        
    return prefs

class IntentParser:
    async def parse_intent(self, text: str, context: dict = None) -> IntentResult:
        t = text.strip()
        
        # 1. Attempt LLM Parsing if API Key exists
        if GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = await model.generate_content_async(
                    f"{SYSTEM_PROMPT}\nUser input: \"{t}\""
                )
                raw_json = response.text.strip()
                if raw_json.startswith("```json"):
                    raw_json = raw_json[7:-3].strip()
                elif raw_json.startswith("```"):
                    raw_json = raw_json[3:-3].strip()
                    
                data = json.loads(raw_json)
                data["raw_text"] = t
                return IntentResult(**data)
            except Exception:
                # LLM failed or timed out; fall back to regex engine
                pass

        # 2. Robust Regex Fallback Engine
        tl = t.lower()
        budget = _extract_budget(t)
        cat = _detect_category(tl)

        # High priority check: Cart Management
        if any(tr in tl for tr in ['clear', 'empty', 'saaf', 'sab hata']):
            return IntentResult(intent="CLEAR_CART", raw_text=t)

        if any(tr in tl for tr in ['show', 'dekho', 'list', 'kya hai', 'whats in', 'dikhao', 'basket']):
            return IntentResult(intent="SHOW_CART", category=cat, raw_text=t)

        if any(tr in tl for tr in ['remove', 'hata', 'delete', 'nikalo', 'mat lena', 'cancel']):
            clean_text = re.sub(r'\b(remove|hata|hatao|delete|nikalo|mat lena|cancel|from cart|from basket)\b', '', tl, flags=re.IGNORECASE).strip()
            return IntentResult(intent="REMOVE_ITEM", items=[{"raw_query": clean_text}], raw_text=t)

        if any(tr in tl for tr in ['alternative', 'substitute', 'replace', 'instead', 'cheaper option', 'badle']):
            return IntentResult(intent="FIND_SUBSTITUTE", raw_text=t)

        # Recommendation vs Add Item disambiguation
        is_recommend_trigger = any(tr in tl for tr in ['recommend', 'suggest', 'best', 'find me', 'top', 'search', 'compare', 'which one'])
        has_decision_spec = bool(budget or cat in ['Laptops', 'Smartphones', 'Electronics'] or 'for' in tl)

        if is_recommend_trigger or (has_decision_spec and not any(w in tl for w in ['add', 'jod', 'daal'])):
            hard = {}
            if budget:
                hard['max_budget'] = budget
            if '16gb' in tl or '16 gb' in tl:
                hard['min_ram_gb'] = 16
            elif '8gb' in tl or '8 gb' in tl:
                hard['min_ram_gb'] = 8

            return IntentResult(
                intent="RECOMMEND",
                category=cat or "Electronics",
                hard_constraints=hard,
                soft_preferences=_extract_soft_preferences(t),
                raw_text=t,
                requested_action="recommend"
            )

        # Standard Add Item
        clean_text = re.sub(r'\b(add|jod|daal|lena hai|buy|get me|aur)\b', '', tl, flags=re.IGNORECASE).strip()
        qty, unit, product = _extract_quantity_and_product(clean_text)
        hard = {'max_budget': budget} if budget else {}

        return IntentResult(
            intent="ADD_ITEM",
            items=[{"raw_query": product, "quantity": qty, "unit": unit}],
            hard_constraints=hard,
            raw_text=t
        )

intent_parser = IntentParser()