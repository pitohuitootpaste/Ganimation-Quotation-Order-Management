from modules.storage import load_data

def view_declined_quotations():
    declined = load_data("declined.json")
    print("\n========== DECLINED QUOTATIONS ==========")

    if not declined:
        print("No declined quotations found.")
        return

    for quotation in declined:

        print("----------------------------------------")
        print(f"Quotation ID: {quotation['quotation_id']}")
        print(f"Customer: {quotation['customer_name']}")
        print(f"Product: {quotation['product_name']}")
        print(f"Quantity: {quotation['quantity']}")
        print(f"Total: PHP {quotation['total_price']:,.2f}")
        print(f"Status: {quotation['status']}")

def view_declined_details():
    declined = load_data("declined.json")

    try:
        quotation_id = int(input("\nEnter Quotation ID: "))
    except ValueError:
        print("Invalid Quotation ID.")
        return

    quotation = next(
        (q for q in declined if q["quotation_id"] == quotation_id),
        None
    )

    if quotation is None:
        print("Quotation not found.")
        return

    print("\n========== QUOTATION DETAILS ==========")
    print(f"Quotation ID: {quotation['quotation_id']}")
    print(f"Customer: {quotation['customer_name']}")
    print(f"Phone: {quotation['phone_number']}")
    print(f"Email: {quotation['email']}")
    print("---------------------------------------")
    print(f"Product: {quotation['product_name']}")
    print(f"Quantity: {quotation['quantity']}")
    print(f"Price Per Product: PHP {quotation['price_per_product']:,.2f}")
    print(f"Discount: {quotation['discount']}%")
    print(f"Subtotal: PHP {quotation['subtotal']:,.2f}")
    print(f"Total: PHP {quotation['total_price']:,.2f}")
    print("---------------------------------------")
    print(f"Rush Order: {quotation['is_rush_order']}")
    print(f"Instructions: {quotation['special_instructions']}")
    print(f"Date Created: {quotation['date_created']}")
    print(f"Date Finalized: {quotation['date_finalized']}")
    print(f"Status: {quotation['status']}")

def quotation_archive_menu():
    while True:
        print("\n================================")
        print("        QUOTATION ARCHIVE")
        print("================================")
        print("1. View Declined Quotations")
        print("2. View Quotation Details")
        print("0. Back")
        print("================================")
        choice = input("Enter choice: ")

        if choice == "1":
            view_declined_quotations()
        elif choice == "2":
            view_declined_details()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")