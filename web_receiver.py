import html
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from modules.responseStore import (
    create_tables,
    get_customer_responses,
    record_decision,
    save_response_link
)


API_KEY = os.getenv("RESPONSE_API_KEY", "")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")


def response_page(title, message, form=None):
    form_html = ""
    if form:
        escaped_token = html.escape(form["token"], quote=True)
        escaped_decision = html.escape(form["decision"], quote=True)
        action_text = "accept" if form["decision"] == "accepted" else "decline"
        form_html = f"""
        <form method="post" action="/respond">
            <input type="hidden" name="token" value="{escaped_token}">
            <input type="hidden" name="decision" value="{escaped_decision}">
            <button type="submit">Confirm {action_text}</button>
        </form>
        """

    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title></head>
<body style="font-family:Arial,sans-serif;max-width:640px;margin:60px auto;padding:0 20px;line-height:1.5">
<h1>{html.escape(title)}</h1><p>{html.escape(message)}</p>{form_html}
</body></html>"""


class ResponseHandler(BaseHTTPRequestHandler):
    def log_message(self, format_string, *args):
        return

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, status, title, message, form=None):
        body = response_page(title, message, form).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        supplied_key = self.headers.get("Authorization", "").removeprefix("Bearer ")
        return bool(API_KEY) and secrets.compare_digest(supplied_key, API_KEY)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        if length <= 0 or length > 65536:
            return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self.send_json(200, {"status": "ok"})
            return

        if parsed.path == "/api/responses":
            if not self.authorized():
                self.send_json(401, {"error": "Not authorized."})
                return
            try:
                self.send_json(200, {"responses": get_customer_responses()})
            except Exception:
                self.send_json(503, {"error": "Could not load customer responses."})
            return

        if parsed.path != "/respond":
            self.send_html(404, "Page not found", "This link is not available.")
            return

        query = parse_qs(parsed.query)
        token = query.get("token", [""])[0]
        decision = query.get("decision", [""])[0]
        if not token or decision not in ("accepted", "declined"):
            self.send_html(400, "Invalid link", "This response link is incomplete.")
            return

        action = "accept" if decision == "accepted" else "decline"
        self.send_html(
            200,
            f"Confirm {action} quotation",
            f"Press the button below to confirm that you want to {action} this quotation.",
            {"token": token, "decision": decision}
        )

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/quotations":
            if not self.authorized():
                self.send_json(401, {"error": "Not authorized."})
                return

            quotation = self.read_json()
            required = ("client_id", "quotation_id")
            if not isinstance(quotation, dict) or any(
                not quotation.get(field) for field in required
            ):
                self.send_json(400, {"error": "Quotation details are incomplete."})
                return
            if (
                not isinstance(quotation["quotation_id"], int)
                or not isinstance(quotation["client_id"], str)
                or len(quotation["client_id"]) > 100
            ):
                self.send_json(400, {"error": "Quotation or computer ID is invalid."})
                return
            if not PUBLIC_BASE_URL:
                self.send_json(503, {"error": "The public service URL is not configured."})
                return

            token = secrets.token_urlsafe(32)
            try:
                save_response_link(quotation, token)
            except ValueError as error:
                self.send_json(409, {"error": str(error)})
                return
            except Exception:
                self.send_json(503, {"error": "Could not save the response link."})
                return

            encoded_token = urlencode({"token": token})
            self.send_json(200, {
                "accept_url": f"{PUBLIC_BASE_URL}/respond?{encoded_token}&decision=accepted",
                "decline_url": f"{PUBLIC_BASE_URL}/respond?{encoded_token}&decision=declined"
            })
            return

        if parsed.path != "/respond":
            self.send_html(404, "Page not found", "This link is not available.")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > 4096:
            self.send_html(400, "Invalid response", "The response could not be submitted.")
            return
        form = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"))
        token = form.get("token", [""])[0]
        decision = form.get("decision", [""])[0]
        if not token or decision not in ("accepted", "declined"):
            self.send_html(400, "Invalid response", "The response could not be submitted.")
            return

        try:
            record_decision(token, decision)
        except (ValueError, LookupError) as error:
            self.send_html(409, "Response not submitted", str(error))
            return
        except Exception:
            self.send_html(503, "Try again later", "The response service is temporarily unavailable.")
            return

        action = "accepted" if decision == "accepted" else "declined"
        self.send_html(200, "Response recorded", f"Thank you. You have {action} this quotation.")


def main():
    if not API_KEY:
        raise RuntimeError("Set the RESPONSE_API_KEY environment variable in Render.")
    if not PUBLIC_BASE_URL:
        raise RuntimeError("Set PUBLIC_BASE_URL to your Render service URL.")

    create_tables()
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), ResponseHandler)
    print(f"Customer response service listening on port {port}.")
    server.serve_forever()


if __name__ == "__main__":
    main()
