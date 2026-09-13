import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sipa_trace.card import TraceCard
from sipa_trace.diff import diff_cards

app = FastAPI()

# Enable CORS for your Vite dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_cards() -> list[TraceCard]:
    cards = []
    try:
        with open("trace.jsonl", "r") as f:
            for line in f:
                if line.strip():
                    cards.append(TraceCard.from_dict(json.loads(line)))
    except FileNotFoundError:
        pass
    return cards

@app.get("/api/trace")
def get_trace():
    cards = load_cards()
    return [c.to_dict() for c in cards]

@app.get("/api/diff")
def get_diff():
    cards = load_cards()
    if len(cards) < 2:
        return None
    # Compare the last two cards
    diff_result = diff_cards(cards[-2], cards[-1])
    # Convert sets/dicts to JSON serializable formats if needed
    return diff_result

@app.get("/api/verify")
def get_verify():
    # Placeholder for sipa_trace.verify.verify() logic
    cards = load_cards()
    if not cards:
        return {"valid": True, "card_count": 0}
    
    # Simple hash verification check
    is_valid = True
    for i in range(1, len(cards)):
        if cards[i].prev_hash != cards[i-1].hash:
            is_valid = False
            break
            
    return {"valid": is_valid, "card_count": len(cards)}