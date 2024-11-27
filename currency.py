#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# currency.py
#
# This file contains the currency conversion functionality
# using an API and custom exchange rates.
#
#################################################################

import requests
from datetime import datetime, timedelta
from decimal import Decimal
from notifications import subject, Notifications
from database import fetch_all_exchange_rates, update_exchange_rate, get_exchange_rate_from_db
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')

API_KEY = config.get('API', 'API_Key')
BASE_CURRENCY = config.get('API', 'Base_Currency')
BASE_API_URL = f"https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}?api_key={API_KEY}"

# Cache to store exchange rates and reduce API calls
exchange_rates_cache = {"rates": {}, "last_updated": None}

# Main menu for currency conversion functionality.
def currency_menu(cnxn):

    cursor = cnxn.cursor()

    while True:
        print("\n" + "=" * 35 + "\n" + "CURRENCY CONVERSION".center(38) + "\n" + "=" * 35 + "\n")
        print("1. API Exchange Rate")
        print("2. Custom Exchange Rate")
        print("3. Back to Main Menu\n")
        print("-" * 35)
        choice = input("Enter your choice: ").strip()
        print("-" * 35)

        if choice == "1":
            amount_input = input("\nEnter the amount in CAD: $").strip()

            if amount_input.replace('.', '', 1).isdigit():

                amount = Decimal(amount_input)
                chosen_currency = input("Enter currency (e.g., CAD, USD, EUR): ").strip().upper()
                exchange_rate = get_exchange_rate(cursor, chosen_currency)
                
                # Perform the conversion
                if exchange_rate and exchange_rate != Decimal("1.0"):
                    converted_amount = amount * exchange_rate
                    print(f"\nAPI exchange rate ({BASE_CURRENCY} to {chosen_currency}): {exchange_rate:.4f}")
                    print(f"Converted Amount: ${converted_amount:,.2f} {chosen_currency}")

                elif chosen_currency == BASE_CURRENCY:
                    print(f"\nAmount remains unchanged in {BASE_CURRENCY}: ${amount:,.2f} {BASE_CURRENCY}")
                
                else:
                    subject.notify(Notifications.exchange_rate_not_found())
            else:
                subject.notify(Notifications.invalid_input())

        elif choice == "2":
        
            amount_input = input("\nEnter the amount in CAD: $").strip()

            # Validate the amount input
            if amount_input.replace('.', '', 1).isdigit():
                amount = Decimal(amount_input)
                chosen_currency = input("Enter currency (e.g., CAD, USD, EUR): ").strip().upper()
                custom_rate_input = input(f"Enter your custom exchange rate for {BASE_CURRENCY} to {chosen_currency}: ").strip()

                # Call the updated custom exchange rate function
                set_custom_exchange_rate(cursor, amount, chosen_currency, custom_rate_input)
            else:
                subject.notify(Notifications.invalid_input())

        elif choice == "3":
            subject.notify(Notifications.returning_to_main_menu())
            break
        else:
            subject.notify(Notifications.invalid_choices_one_to_three())


# Fetch and cache all exchange rates from the API
def fetch_and_cache_exchange_rates():

    global exchange_rates_cache
    response = requests.get(BASE_API_URL)

    # If the API call is successful, update the cache
    if response.status_code == 200:
        data = response.json()
        exchange_rates = {k: Decimal(str(v)) for k, v in data.get("rates", {}).items()}
        last_updated = datetime.now()

        # Update the cache
        exchange_rates_cache["rates"] = exchange_rates
        exchange_rates_cache["last_updated"] = last_updated

        return exchange_rates
    else:
        subject.notify(Notifications.exchange_rate_not_found(BASE_CURRENCY))
        return None

#Fetch the exchange rate for the specified currency. Cache and store rates in the database.
def get_exchange_rate(cursor, chosen_currency):

    # Check if the rate exists in cache
    if exchange_rates_cache["rates"] and (
        datetime.now() - exchange_rates_cache["last_updated"] <= timedelta(hours=24)
    ):
        return exchange_rates_cache["rates"].get(chosen_currency)

    # If not in cache, fetch all rates from API and update cache
    exchange_rates = fetch_and_cache_exchange_rates()
    
    # If the API call is successful, update the database with the new rates
    if exchange_rates:
        rate = exchange_rates.get(chosen_currency)
        if rate:
            last_updated = exchange_rates_cache["last_updated"]
            update_exchange_rate(cursor, BASE_CURRENCY, chosen_currency, rate, last_updated)
            return rate

    # Fallback to database if API fails
    print(f"API unavailable, checking database for {chosen_currency} rate...")
    return get_exchange_rate_from_db(cursor, BASE_CURRENCY, chosen_currency) or Decimal("1.0")


# Converts an amount from the base currency (CAD) to the chosen currency.
def currency_conversion(cursor, amount, chosen_currency):
    # Get the exchange rate for the chosen currency
    rate = get_exchange_rate(cursor, chosen_currency)
    # Perform the conversion
    if rate:
        # Convert the amount to the chosen currency
        return Decimal(str(amount)) * rate
    else:
        subject.notify(Notifications.conversion_failed())
        return None
    
# Validates the user's chosen currency

def validate_currency(cursor):

    while True:
        chosen_currency = input("\n" + "Enter currency (e.g., CAD, USD, EUR): ").strip().upper()
        if chosen_currency.isalpha():
            # Check if the currency is supported
            exchange_rate = get_exchange_rate(cursor, chosen_currency)
            # If the currency is supported, return it
            if exchange_rate != Decimal("1.0") or chosen_currency == BASE_CURRENCY:
                return chosen_currency
            else:
                subject.notify(Notifications.exchange_rate_not_found())
        else:
            subject.notify(Notifications.invalid_currency())

# Adjust custom exchange rate realistically based on actual exchange rates.

def set_custom_exchange_rate(cursor, amount, chosen_currency, custom_rate_input):
    # Validate the chosen currency and custom rate
    if not chosen_currency.isalpha():
        subject.notify(Notifications.invalid_currency())
        return None

    if not custom_rate_input.replace('.', '', 1).isdigit():
        subject.notify(Notifications.invalid_currency_rate())
        return None

    custom_rate = Decimal(custom_rate_input)
    if custom_rate <= 0:
        subject.notify(Notifications.exchange_rate_greater())
        return None

    # Get the actual exchange rate and adjust the custom rate
    actual_rate = get_exchange_rate(cursor, chosen_currency)
    adjusted_custom_rate = actual_rate / custom_rate
    # Perform the conversion
    converted_amount = Decimal(amount) * adjusted_custom_rate

    # Print the custom exchange rate and converted amount
    print(f"\nCustom exchange rate ({BASE_CURRENCY} to {chosen_currency}): {adjusted_custom_rate:.4f}")
    print(f"Converted Amount: ${converted_amount:,.2f} {chosen_currency}")

    return converted_amount

# Allow user to view the transaction in another currency

def handle_currency_conversion(cnxn, transaction_date, amount, category, description):

    cursor = cnxn.cursor()

    while True:

        convert_choice = input("\nDo you want to convert this transaction to another currency? (yes/no): ").strip().lower()
            
        if convert_choice in ["yes", "y"]:

            chosen_currency = validate_currency(cursor)
            exchange_rate = get_exchange_rate(cursor, chosen_currency)
            converted_amount = currency_conversion(cursor, amount, chosen_currency)
            
            if converted_amount is not None:
                exchange_rate = get_exchange_rate(cursor, chosen_currency)

                print("\n" + "-" * 35)
                print(f"   Transaction Summary in {chosen_currency}")
                print("-" * 35)
                print(f"Date:                 {transaction_date.strftime('%m-%d-%Y')}")
                print(f"Original Amount:      ${float(amount):,.2f} {BASE_CURRENCY}")
                print(f"Converted Amount:     ${converted_amount:,.2f} {chosen_currency}")
                print(f"Exchange Rate:        1 {BASE_CURRENCY} = {exchange_rate:.4f} {chosen_currency}")
                print(f"Category:             {category.capitalize()}")
                print(f"Description:          {description.capitalize()}")
                print("-" * 35)
                subject.notify(Notifications.returning_to_main_menu())
            else:
                subject.notify(Notifications.conversion_failed())
            break

        elif convert_choice in ["no", "n"]:
            print("\n" + "-" * 35)
            subject.notify(Notifications.returning_to_main_menu())
            break

        else:
            subject.notify(Notifications.invalid_yes_or_no())
