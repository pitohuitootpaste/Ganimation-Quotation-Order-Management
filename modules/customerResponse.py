from modules.storage import load_data, save_data
from datetime import datetime

def customer_response():

    quotations = load_data("quotations.json")
    print("\n================================")
    print("       CUSTOMER RESPONSE")
    print("================================")
    finalized = [
        q for q in quotations
        if q["status"] == "Finalized"
    ]

    if not finalized:
        print("No finalized quotations awaiting response.")
        return

    for quotation in finalized:
        print("--------------------------------")
        print(f"Quotation ID: {quotation['quotation_id']}")
        print(f"Customer: {quotation['customer_name']}")
        print(f"Product: {quotation['product_name']}")
        print(f"Total: PHP {quotation['total_price']:,.2f}")

    print("--------------------------------")

    try:
        quotation_id = int(input("\nEnter Quotation ID: "))
    except ValueError:
        print("Invalid quotation ID.")
        return

    quotation = next(
        (q for q in finalized if q["quotation_id"] == quotation_id),
        None
    )

    if quotation is None:
        print("Quotation not found.")
        return

    print("\n1. Accept Quotation")
    print("2. Decline Quotation")
    print("0. Cancel")
    choice = input("Enter choice: ")

    if choice == "1":

        orders = load_data("orders.json")
        order_id = max(
            [o["order_id"] for o in orders],
            default=0
        ) + 1
        order = quotation.copy()
        order["order_id"] = order_id
        order["date_accepted"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        order["payment_status"] = "Pending"
        order["order_status"] = "Pending"
        order["status"] = "Accepted"
        orders.append(order)
        save_data("orders.json", orders)
        quotations.remove(quotation)
        save_data("quotations.json", quotations)
        print("\nQuotation accepted!")
        print(f"New Order ID: {order_id}")
        print("Order successfully created.")

    elif choice == "2":

        confirm = input(
            "Are you sure you want to decline this quotation? (Y/N): "
        ).lower()

        if confirm != "y":
            print("Action cancelled.")
            return

        declined = load_data("declined.json")
        quotation["status"] = "Declined"
        declined.append(quotation)
        save_data("declined.json", declined)
        quotations.remove(quotation)
        save_data("quotations.json", quotations)
        print("\nQuotation declined.")
        print("Moved to quotation archive.")

    elif choice == "0":
        print("Action cancelled.")

    else:
        print("Invalid choice.")
