from modules.createQuotation import create_quotation
from modules.pendingQuotations import pending_quotations_menu
from modules.customerResponse import customer_response
from modules.order import order_management_menu
from modules.quotationArchive import quotation_archive_menu
from modules.responseClient import sync_customer_responses

def main():
    sync_customer_responses(show_message=True)

    while True:

        print("\n================================")
        print("    PRINTING SHOP MANAGEMENT")
        print("================================")
        print("1. Create Quotation")
        print("2. Quotation Workspace")
        print("3. Order Management")
        print("4. Quotation Archive")
        print("5. Customer Response (TEMP)")
        print("0. Exit")
        print("================================")
        choice = input("Enter choice: ")
        sync_customer_responses()

        if choice == "1":
            create_quotation()

        elif choice == "2":
            pending_quotations_menu()

        elif choice == "3":
            order_management_menu()

        elif choice == "4":
            quotation_archive_menu()

        elif choice == "5":
            customer_response()

        elif choice == "0":
            print("Exiting Printing Shop System...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
