import json
from pathlib import Path

def load_config() -> dict:
    path = path = Path(__file__).parent / "config.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

