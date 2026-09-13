import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sipa_trace.card import TraceCard
from sipa_trace.diff import diff_cards
from sipa_trace.verify import verify as trace_verify

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
    result = trace_verify("trace.jsonl")
    return {
        "valid": result.ok, 
        "card_count": result.count, 
        "problems": result.problems
    }