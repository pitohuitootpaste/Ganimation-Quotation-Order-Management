import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from modules.settings import RESPONSE_API_KEY, RESPONSE_SERVICE_URL
from modules.storage import load_data, save_data


CLIENT_ID_FILE = Path(__file__).resolve().parent.parent / "data" / ".response_client_id"


def get_client_id():
    CLIENT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CLIENT_ID_FILE.exists():
        return CLIENT_ID_FILE.read_text(encoding="utf-8").strip()

    client_id = uuid.uuid4().hex
    CLIENT_ID_FILE.write_text(client_id, encoding="utf-8")
    return client_id


def _api_request(path, method="GET", body=None):
    if not RESPONSE_SERVICE_URL or not RESPONSE_API_KEY:
        raise RuntimeError(
            "Customer response links are not configured on this computer yet."
        )

    data = None
    headers = {"Authorization": f"Bearer {RESPONSE_API_KEY}"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{RESPONSE_SERVICE_URL}{path}",
        data=data,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            details = json.loads(error.read().decode("utf-8"))
            message = details.get("error", "The hosted service returned an error.")
        except (ValueError, UnicodeDecodeError):
            message = "The hosted service returned an error."
        raise RuntimeError(message) from error
    except URLError as error:
        raise RuntimeError("Could not connect to the hosted response service.") from error


def create_response_links(quotation):
    if not RESPONSE_SERVICE_URL or not RESPONSE_API_KEY:
        raise RuntimeError(
            "Customer response links are not configured on this computer yet."
        )

    payload = json.dumps(
        {
            "client_id": get_client_id(),
            "quotation_id": quotation["quotation_id"]
        },
        separators=(",", ":")
    ).encode("utf-8")
    encoded_payload = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    signature = hmac.new(
        RESPONSE_API_KEY.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256
    ).hexdigest()
    token = f"{encoded_payload}.{signature}"
    return (
        f"{RESPONSE_SERVICE_URL}/respond?token={token}&decision=accepted",
        f"{RESPONSE_SERVICE_URL}/respond?token={token}&decision=declined"
    )


def sync_customer_responses(show_message=False):
    if not RESPONSE_SERVICE_URL or not RESPONSE_API_KEY:
        return

    try:
        results = _api_request("/api/responses")
    except RuntimeError as error:
        if show_message:
            print(f"Could not check customer responses: {error}")
        return

    quotations = load_data("quotations.json")
    orders = load_data("orders.json")
    declined = load_data("declined.json")
    handled = 0
    client_id = get_client_id()

    for response in results.get("responses", []):
        if response.get("client_id") != client_id:
            continue

        quotation = next(
            (
                item for item in quotations
                if item["quotation_id"] == response["quotation_id"]
            ),
            None
        )

        if quotation is None or quotation.get("status") != "Finalized":
            continue

        if response["decision"] == "accepted":
            if any(order.get("quotation_id") == quotation["quotation_id"] for order in orders):
                continue

            order_id = max(
                (order.get("order_id", 0) for order in orders),
                default=0
            ) + 1
            order = quotation.copy()
            order["order_id"] = order_id
            order["date_accepted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order["payment_status"] = "Pending"
            order["order_status"] = "Pending"
            order["status"] = "Accepted"
            orders.append(order)
        elif response["decision"] == "declined":
            if not any(item.get("quotation_id") == quotation["quotation_id"] for item in declined):
                declined_quotation = quotation.copy()
                declined_quotation["status"] = "Declined"
                declined.append(declined_quotation)

        quotations.remove(quotation)
        handled += 1

    if handled:
        save_data("quotations.json", quotations)
        save_data("orders.json", orders)
        save_data("declined.json", declined)
        if show_message:
            print(f"Synced {handled} customer response(s) from Render.")
    elif show_message:
        print("No new customer responses to sync.")
