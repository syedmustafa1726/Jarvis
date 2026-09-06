import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_db", "memory.json")

def ensure_file():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({"conversations": [], "facts": []}, f)

def save_message(role: str, content: str):
    ensure_file()
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    data["conversations"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    data["conversations"] = data["conversations"][-100:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def save_fact(fact: str):
    ensure_file()
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    data["facts"].append({
        "fact": fact,
        "timestamp": datetime.now().isoformat()
    })
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def get_relevant_memory(query: str, n_results: int = 3) -> str:
    try:
        ensure_file()
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        conversations = data["conversations"][-10:]
        if conversations:
            memory = "\n".join([f"{c['role']}: {c['content']}" for c in conversations])
            return f"Recent conversations:\n{memory}"
    except Exception:
        pass
    return ""

def get_all_facts() -> str:
    try:
        ensure_file()
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        if data["facts"]:
            return "Facts about Mustafa:\n" + "\n".join([f["fact"] for f in data["facts"]])
    except Exception:
        pass
    return ""
