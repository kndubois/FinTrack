#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# transaction.py
#
# This file contains logging a transaction.
#
#################################################################
 
from datetime import datetime
from database import add_transaction
from currency import handle_currency_conversion
from notifications import subject, Notifications
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')
BASE_CURRENCY = config.get('API', 'Base_Currency')


# Main menu for logging a transaction
def transaction_menu(cnxn):

    print("\n" + "=" * 35 + "\n" + "LOG A TRANSACTION".center(38) + "\n" + "=" * 35 + "\n")
    
    transaction_date = get_valid_date()
    amount = get_valid_amount(f"Amount ({BASE_CURRENCY}):         $", Notifications.invalid_amount())
    category = get_valid_input("Category:             ", Notifications.invalid_category())
    description = input("Description:          ").strip() or "N/A"

    add_transaction(cnxn, transaction_date, amount, category, description) # add the transaction to the database
    print_transaction_summary(transaction_date, amount, category, description) # print the transaction summary

    handle_currency_conversion(cnxn, transaction_date, amount, category, description) # currency conversion

# Validate the date input

def get_valid_date():

    while True:

        print("Enter the transaction details:")
        print("-" * 35)

        date_input = input("Date (MM-DD-YYYY):    ").strip()
        
        # Check if the date is in the correct format
        if date_input.count('-') == 2:
            month, day, year = date_input.split('-')
            if month.isdigit() and day.isdigit() and year.isdigit():
                month, day, year = int(month), int(day), int(year)
                
                #  Check if the date is valid
                if 1 <= month <= 12 and 1 <= day <= 31:
                    if len(str(year)) != 4:  # forces year length to be 4 digits
                        subject.notify(Notifications.invalid_transaction_year())
                        continue
                    month, day, year = int(month), int(day), int(year)
                # Check if the date is in the future
                if 1 <= month <= 12 and 1 <= day <= 31:
                    if year > 2024:
                        subject.notify(Notifications.invalid_future_transaction_date())
                        continue
                    # Check if the date is in the past
                    elif year < 2024: 
                        confirm = input("\n" + Notifications.past_transaction_warning()).strip().lower()
                        if confirm in ["yes", "y"]:
                            return datetime(year, month, day)
                        else:
                            continue
                    else: 
                        return datetime(year, month, day)

        subject.notify(Notifications.invalid_transaction_date())

# Validate the amount input
def get_valid_amount(prompt, error_message):

    while True:
        amount_input = input(prompt).strip()
        if amount_input.replace('.', '', 1).isdigit():
            return float(amount_input)
        error_message()

# Validate the category input
def get_valid_input(prompt, error_message):
    
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        print(error_message)

# Print the transaction summary        

def print_transaction_summary(transaction_date, amount, category, description):
    print("\nTransaction Logged Successfully!")
    print("-" * 35)
    print(f"Transaction Summary".center(35))
    print("-" * 35)
    print(f"Date:                 {transaction_date.strftime('%m-%d-%Y')}")
    print(f"Amount:               ${amount:,.2f} {BASE_CURRENCY}")
    print(f"Category:             {category.capitalize()}")
    print(f"Description:          {description.capitalize()}")
    print("-" * 35)