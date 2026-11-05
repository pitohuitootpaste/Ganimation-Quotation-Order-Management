import json
import threading
from pathlib import Path


RESPONSE_FILE = Path(__file__).resolve().parent.parent / "data" / "customer_responses.json"
FILE_LOCK = threading.Lock()


def _read_responses():
    if not RESPONSE_FILE.exists():
        return []

    with RESPONSE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_responses(responses):
    RESPONSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = RESPONSE_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(responses, file, indent=4)
    temporary_file.replace(RESPONSE_FILE)


def record_decision(client_id, quotation_id, decision):
    with FILE_LOCK:
        responses = _read_responses()
        existing = next(
            (
                item for item in responses
                if item["client_id"] == client_id
                and item["quotation_id"] == quotation_id
            ),
            None
        )

        if existing:
            raise ValueError("A response has already been submitted for this quotation.")

        responses.append({
            "client_id": client_id,
            "quotation_id": quotation_id,
            "decision": decision
        })
        _write_responses(responses)


def get_customer_responses():
    with FILE_LOCK:
        return _read_responses()
