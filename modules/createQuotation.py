from modules.storage import load_data, save_data
from datetime import datetime

def create_quotation():
    print("\n================================")
    print("         CREATE QUOTATION")
    print("================================")
    while True:
        customer_name = input("Customer Name: ").strip()
        if customer_name:
            break
        print("Customer name cannot be empty.")

    phone_number = input("Phone Number (Optional): ").strip()

    while True:
        email = input("Email Address: ").strip()
        if email.count("@") == 1 and "." in email.rsplit("@", 1)[1]:
            break
        print("Please enter a valid email address.")

    while True:
        product_name = input("Product / Order Name: ").strip()
        if product_name:
            break
        print("Product / order name cannot be empty.")

    while True:
        try:
            quantity = int(input("Quantity: "))
            if quantity <= 0:
                print("Quantity must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid whole number.")

    while True:
        try:
            price_per_product = float(input("Price Per Product: "))
            if price_per_product < 0:
                print("Price cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid price.")

    while True:
        try:
            discount = float(input("Discount Percentage (0-100): "))
            if discount < 0 or discount > 100:
                print("Discount must be between 0 and 100.")
                continue
            break
        except ValueError:
            print("Please enter a valid percentage.")

    while True:
        rush_input = input("Rush Order? (Y/N): ").strip().lower()
        if rush_input == "y":
            is_rush_order = True
            break
        elif rush_input == "n":
            is_rush_order = False
            break
        else:
            print("Please enter Y or N.")

    special_instructions = input("Special Instructions (Optional): ")
    subtotal = quantity * price_per_product
    discount_amount = subtotal * (discount / 100)
    total_price = subtotal - discount_amount
    quotations = load_data("quotations.json")
    orders = load_data("orders.json")
    declined = load_data("declined.json")
    all_ids = []
    all_ids.extend(q["quotation_id"] for q in quotations)
    all_ids.extend(o["quotation_id"] for o in orders)
    all_ids.extend(d["quotation_id"] for d in declined)
    quotation_id = max(all_ids, default=0) + 1
    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    quotation = {
        "quotation_id": quotation_id,
        "customer_name": customer_name,
        "phone_number": phone_number,
        "email": email,
        "product_name": product_name,
        "quantity": quantity,
        "price_per_product": price_per_product,
        "discount": discount,
        "is_rush_order": is_rush_order,
        "special_instructions": special_instructions,
        "subtotal": round(subtotal, 2),
        "total_price": round(total_price, 2),
        "status": "Draft",
        "date_created": date_created,
        "date_finalized": None
    }
    quotations.append(quotation)
    save_data("quotations.json", quotations)
    print("\n================================")
    print("       QUOTATION CREATED")
    print("================================")
    print(f"Quotation ID: {quotation_id}")
    print(f"Customer: {customer_name}")
    print(f"Product: {product_name}")
    print(f"Quantity: {quantity}")
    print(f"Subtotal: PHP {subtotal:,.2f}")
    print(f"Discount: {discount}%")
    print(f"Total Price: PHP {total_price:,.2f}")
    print(f"Status: Draft")
    print("================================")
