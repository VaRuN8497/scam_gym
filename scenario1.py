import re

# Scenario 1: fake parcel / "digital arrest" call. Every name and detail is
# fictional. The lines are short drill prompts for recognition, not a real script.
BEATS = [
    {"name": "hook",
     "line": "This is Officer Rakesh Verma, Mumbai Parcel Cell. A parcel in your name has a problem."},
    {"name": "fear",
     "line": "Your Aadhaar is linked to this case. You may face arrest."},
    {"name": "isolate",
     "line": "Do not tell anyone and do not hang up. This case is confidential."},
    {"name": "rush",
     "line": "You have two minutes. Decide now."},
    {"name": "pay_share",
     "line": "To close the case, read me the verification code sent to your phone."},
]

NUMBER_WORDS = {"zero", "one", "two", "three", "four", "five",
                "six", "seven", "eight", "nine"}
REFUSAL_WORDS = {"not", "never", "no", "refuse", "dont", "don't", "wont", "won't"}
GOOD_MOVES = {"asked_proof", "callback", "helpline", "tell_family", "refused"}


def detect_move(transcript: str) -> str:
    """Classify what the player just did. Returns a move label."""
    text = transcript.lower().strip()
    if not text:
        return "silence"

    words = re.findall(r"[a-z0-9']+", text)
    digit_count = sum(len(w) for w in words if w.isdigit())
    number_words = sum(1 for w in words if w in NUMBER_WORDS)
    refused = any(w in REFUSAL_WORDS for w in words)

    if (digit_count >= 4 or number_words >= 4) and not refused:
        return "shared_code"
    if "hang up" in text or "hanging up" in text:
        return "hang_up"
    if "1930" in text or "cyber" in text:
        return "helpline"
    if "call back" in text or "official number" in text:
        return "callback"
    if "proof" in text or "who are you" in text or "badge" in text:
        return "asked_proof"
    if any(w in text for w in ("family", "parents", "mother", "father", "tell my")):
        return "tell_family"
    if refused:
        return "refused"
    if any(w in words for w in ("okay", "yes", "fine", "transfer", "pay")):
        return "complied"
    return "other"


def new_call() -> dict:
    return {"beat": 0, "score": 100, "outcome": None, "line": BEATS[0]["line"]}


def step(state: dict, move: str) -> dict:
    """Apply one player move and return the updated state."""
    if move == "hang_up":
        state["outcome"] = "Hung up in time"
        state["line"] = ""
        return state

    if move == "shared_code":
        state["score"] -= 50
        state["outcome"] = "Fell for it"
        state["line"] = ""
        return state

    if move in GOOD_MOVES:
        state["score"] = min(100, state["score"] + 5)
    elif move == "complied":
        state["score"] -= 25
    else:
        state["score"] -= 5

    state["beat"] += 1
    if state["beat"] >= len(BEATS):
        state["outcome"] = "Survived"
        state["line"] = ""
    else:
        state["line"] = BEATS[state["beat"]]["line"]
    return state


if __name__ == "__main__":
    print("SIMULATION: fake call, all data is fake. Type what you would say.\n")
    state = new_call()
    print("Scammer:", state["line"])
    while state["outcome"] is None:
        said = input("You: ")
        move = detect_move(said)
        state = step(state, move)
        print(f"  [move={move}, score={state['score']}]")
        if state["outcome"] is None:
            print("Scammer:", state["line"])
    print("\nOutcome:", state["outcome"], "| Score:", state["score"])