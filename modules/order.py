from modules.storage import load_data, save_data


def view_orders():

    orders = load_data("orders.json")
    print("\n========== ALL ORDERS ==========")

    if not orders:
        print("No orders found.")
        return

    for order in orders:

        print("--------------------------------")
        print(f"Order ID: {order['order_id']}")
        print(f"Quotation ID: {order['quotation_id']}")
        print(f"Customer: {order['customer_name']}")
        print(f"Product: {order['product_name']}")
        print(f"Total: PHP {order['total_price']:,.2f}")
        print(f"Payment: {order['payment_status']}")
        print(f"Production: {order['order_status']}")

def view_pending_orders():

    orders = load_data("orders.json")
    pending = [
        order for order in orders
        if order["order_status"] != "Completed"
    ]
    print("\n========== PENDING ORDERS ==========")

    if not pending:
        print("No pending orders found.")
        return

    for order in pending:

        print("--------------------------------")
        print(f"Order ID: {order['order_id']}")
        print(f"Customer: {order['customer_name']}")
        print(f"Product: {order['product_name']}")
        print(f"Total: PHP {order['total_price']:,.2f}")
        print(f"Payment: {order['payment_status']}")
        print(f"Production: {order['order_status']}")

def view_completed_orders():

    orders = load_data("orders.json")
    completed = [
        order for order in orders
        if order["order_status"] == "Completed"
    ]
    print("\n========== COMPLETED ORDERS ==========")

    if not completed:
        print("No completed orders found.")
        return

    for order in completed:

        print("--------------------------------")
        print(f"Order ID: {order['order_id']}")
        print(f"Customer: {order['customer_name']}")
        print(f"Product: {order['product_name']}")
        print(f"Total: PHP {order['total_price']:,.2f}")
        print(f"Payment: {order['payment_status']}")
        print(f"Production: {order['order_status']}")

def view_order_details():

    orders = load_data("orders.json")

    try:
        order_id = int(input("\nEnter Order ID: "))
    except ValueError:
        print("Invalid Order ID.")
        return

    order = next(
        (o for o in orders if o["order_id"] == order_id),
        None
    )

    if order is None:
        print("Order not found.")
        return

    print("\n========== ORDER DETAILS ==========")
    print(f"Order ID: {order['order_id']}")
    print(f"Quotation ID: {order['quotation_id']}")
    print(f"Customer: {order['customer_name']}")
    print(f"Phone: {order['phone_number']}")
    print(f"Email: {order['email']}")
    print("-----------------------------------")
    print(f"Product: {order['product_name']}")
    print(f"Quantity: {order['quantity']}")
    print(f"Price Per Product: PHP {order['price_per_product']:,.2f}")
    print(f"Discount: {order['discount']}%")
    print(f"Subtotal: PHP {order['subtotal']:,.2f}")
    if "rush_fee" in order:
        print(f"Rush Surcharge: PHP {order['rush_fee']:,.2f}")
    print(f"Total: PHP {order['total_price']:,.2f}")
    print("-----------------------------------")
    print(f"Rush Order: {order['is_rush_order']}")
    print(f"Instructions: {order['special_instructions']}")
    print("-----------------------------------")
    print(f"Date Accepted: {order['date_accepted']}")
    print(f"Payment Status: {order['payment_status']}")
    print(f"Production Status: {order['order_status']}")

def update_payment_status():

    orders = load_data("orders.json")

    try:
        order_id = int(input("\nEnter Order ID: "))
    except ValueError:
        print("Invalid Order ID.")
        return

    order = next(
        (o for o in orders if o["order_id"] == order_id),
        None
    )

    if order is None:
        print("Order not found.")
        return

    print("\n========== PAYMENT STATUS ==========")
    print(f"Current Status: {order['payment_status']}")
    print("1. Pending")
    print("2. Paid")
    choice = input("Select new status: ")

    if choice == "1":
        order["payment_status"] = "Pending"

    elif choice == "2":
        order["payment_status"] = "Paid"

    else:
        print("Invalid choice.")
        return

    save_data("orders.json", orders)
    print("Payment status updated successfully!")

def update_production_status():

    orders = load_data("orders.json")

    try:
        order_id = int(input("\nEnter Order ID: "))
    except ValueError:
        print("Invalid Order ID.")
        return

    order = next(
        (o for o in orders if o["order_id"] == order_id),
        None
    )

    if order is None:
        print("Order not found.")
        return

    print("\n========== PRODUCTION STATUS ==========")
    print(f"Current Status: {order['order_status']}")
    print("1. Pending")
    print("2. In Progress")
    print("3. Completed")
    choice = input("Select new status: ")

    if choice == "1":
        order["order_status"] = "Pending"

    elif choice == "2":
        order["order_status"] = "In Progress"

    elif choice == "3":
        order["order_status"] = "Completed"

    else:
        print("Invalid choice.")
        return

    save_data("orders.json", orders)
    print("Production status updated successfully!")

def order_management_menu():

    while True:

        print("\n================================")
        print("         ORDER MANAGEMENT")
        print("================================")
        print("1. View All Orders")
        print("2. View Pending Orders")
        print("3. View Completed Orders")
        print("4. View Order Details")
        print("5. Update Payment Status")
        print("6. Update Production Status")
        print("0. Back")
        print("================================")
        choice = input("Enter choice: ")

        if choice == "1":
            view_orders()

        elif choice == "2":
            view_pending_orders()

        elif choice == "3":
            view_completed_orders()

        elif choice == "4":
            view_order_details()

        elif choice == "5":
            update_payment_status()

        elif choice == "6":
            update_production_status()

        elif choice == "0":
            break

        else:
            print("Invalid choice.")
