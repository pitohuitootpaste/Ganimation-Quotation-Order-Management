import base64
from email.message import EmailMessage
from pathlib import Path

from modules.settings import GMAIL_SENDER_EMAIL
from modules.responseClient import register_response_links
from modules.storage import load_data


PROJECT_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = PROJECT_DIR / "credentials.json"
TOKEN_FILE = PROJECT_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ModuleNotFoundError:
        print("Google's Gmail libraries are missing. Run: python -m pip install -r requirements.txt")
        return None

    credentials = None

    if TOKEN_FILE.exists():
        try:
            credentials = Credentials.from_authorized_user_file(
                str(TOKEN_FILE),
                SCOPES
            )
        except (OSError, ValueError):
            print("Could not read token.json. Delete it and authorize Gmail again.")
            return None

    try:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        if not credentials or not credentials.valid:
            if not CREDENTIALS_FILE.exists():
                print("credentials.json is missing from the project folder.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )
            credentials = flow.run_local_server(port=0)
            TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
    except Exception as error:
        print(f"Gmail sign-in failed: {error}")
        return None

    try:
        TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
        return build("gmail", "v1", credentials=credentials)
    except Exception as error:
        print(f"Could not connect to Gmail: {error}")
        return None


def send_finalized_quotation_email():
    quotations = load_data("quotations.json")
    finalized = [
        quotation for quotation in quotations
        if quotation["status"] == "Finalized"
    ]

    print("\n========== EMAIL FINALIZED QUOTATION ==========")

    if not finalized:
        print("No finalized quotations found.")
        return

    for quotation in finalized:
        print("----------------------------------------")
        print(f"Quotation ID: {quotation['quotation_id']}")
        print(f"Customer: {quotation['customer_name']}")
        print(f"Email: {quotation['email']}")
        print(f"Product: {quotation['product_name']}")
        print(f"Total: PHP {quotation['total_price']:,.2f}")

    try:
        quotation_id = int(input("\nEnter Quotation ID to email: "))
    except ValueError:
        print("Invalid Quotation ID.")
        return

    quotation = next(
        (item for item in finalized if item["quotation_id"] == quotation_id),
        None
    )

    if quotation is None:
        print("Finalized quotation not found.")
        return

    recipient = quotation.get("email", "").strip()
    if not recipient:
        print("This quotation does not have an email address.")
        return

    print(f"\nSend Quotation {quotation_id} to {recipient}?")
    confirm = input("Send email? (Y/N): ").strip().lower()
    if confirm != "y":
        print("Email cancelled.")
        return

    service = get_gmail_service()
    if service is None:
        return

    try:
        accept_url, decline_url = register_response_links(quotation)
    except RuntimeError as error:
        print(f"Email was not sent: {error}")
        return

    special_instructions = quotation.get("special_instructions") or "None"
    email_text = f"""Hello {quotation['customer_name']},

Here is your finalized quotation.

Quotation ID: {quotation_id}
Product / Order: {quotation['product_name']}
Quantity: {quotation['quantity']}
Price per product: PHP {quotation['price_per_product']:,.2f}
Discount: {quotation['discount']}%
Subtotal: PHP {quotation['subtotal']:,.2f}
Total: PHP {quotation['total_price']:,.2f}
Rush order: {"Yes" if quotation['is_rush_order'] else "No"}
Special instructions: {special_instructions}

To accept this quotation, open this link:
{accept_url}

To decline this quotation, open this link:
{decline_url}

After opening a link, confirm your choice on the page.

Thank you,
Printing Shop"""

    message = EmailMessage()
    message["To"] = recipient
    message["From"] = GMAIL_SENDER_EMAIL
    message["Subject"] = f"Quotation for {quotation['product_name']}"
    message.set_content(email_text)
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    try:
        result = service.users().messages().send(
            userId="me",
            body={"raw": encoded_message}
        ).execute()
    except Exception as error:
        print(f"Email could not be sent: {error}")
        return

    print("Email sent successfully.")
    if result.get("id"):
        print(f"Gmail message ID: {result['id']}")
