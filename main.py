#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# main.py 
#
# This file contains the main menu for the budgeting application.
#
#################################################################

from database import create_connection, close_connection
from transaction import transaction_menu
from budget import budget_menu
from report import report_menu
from goals import goals_menu
from currency import currency_menu
from notifications import subject, Notifications

# start of the program
def main_menu():

    cnxn = create_connection() # establishes database connection
    if not cnxn:
        print("Error: Unable to establish a connection ")
        return
    
    while True:
        subject.notify(Notifications.welcome())
        print("\nPlease select an option:")
        print("1. Log a Transaction")
        print("2. Create a Budget")
        print("3. Savings Goals")
        print("4. View Reports")
        print("5. Currency Conversion")
        print("6. Exit\n")
        print("-" * 35)
        choice = input("Enter your choice: ").strip()
        print("-" * 35)
        
        if choice.isdigit() and 1 <= int(choice) <= 6:
            choice = int(choice)

            if choice == 1:
                transaction_menu(cnxn)
            elif choice == 2:
                budget_menu(cnxn)
            elif choice == 3:
                goals_menu(cnxn)
            elif choice == 4:
                report_menu(cnxn)
            elif choice == 5:
                currency_menu(cnxn)
            elif choice == 6:
                subject.notify(Notifications.goodbye())
                break
        else:
            subject.notify(Notifications.invalid_choices_one_to_six())
            input("Press Enter to return to the main menu.\n")

    close_connection(cnxn) 

main_menu()
