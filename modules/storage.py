from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def load_data(filename):

    path = DATA_DIR / filename

    if not path.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text("[]", encoding="utf-8")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def save_data(filename, data):

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
