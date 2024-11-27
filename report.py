#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# report.py
#
# This file contains the main menu for viewing and 
# generating reports.
#
#################################################################

from datetime import datetime
from currency import currency_conversion, get_exchange_rate, validate_currency
from database import get_transactions, get_budget, get_savings_goals_summary, get_goals, get_all_reports, add_report, get_report_by_id
from notifications import subject, Notifications
from decimal import Decimal
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')
BASE_CURRENCY = config.get('API', 'Base_Currency')

def report_menu(cnxn):
    
    while True:
        print("\n" + "=" * 35 + "\n" + "REPORT MENU".center(38) + "\n" + "=" * 35 + "\n")
        print("1. Transaction Report")
        print("2. Budget Report")
        print("3. Savings Goals Report")
        print("4. Generate General Report")
        print("5. View Saved Reports")
        print("6. Back to Main Menu\n")
        print("-" * 35)
        choice = input("Enter your choice: ").strip()
        print("-" * 35)

        if choice == "1":
            generate_transaction_report(cnxn)
        elif choice == "2":
            generate_budget_report(cnxn)
        elif choice == "3":
            chosen_currency = validate_currency
            generate_savings_goals_summary(cnxn, chosen_currency)
        elif choice == "4":
            generate_general_report(cnxn)
        elif choice == "5":
            view_saved_reports(cnxn)
        elif choice == "6":
            subject.notify(Notifications.returning_to_main_menu())
            break
        else:
            subject.notify(Notifications.invalid_choice())


# Generate a report of all transactions with currency conversion.
def generate_transaction_report(cnxn):
    
    cursor = cnxn.cursor()
    chosen_currency = validate_currency(cursor)
    conversion_rate = get_exchange_rate(cursor, chosen_currency)
    
    # If the conversion rate is not found, return to the menu
    if conversion_rate == Decimal("1.0") and chosen_currency != BASE_CURRENCY:
        return

    print("\n" + "=" * 10 + f" TRANSACTION REPORT " + "=" * 10 + "\n")
    print("-" * 74)
    print(f"| {'Date':<11} | {'Amount':<16} | {'Category':<16} | {'Description':<18} |")
    print("-" * 74)

    transactions = get_transactions(cnxn)

    if not transactions:
        subject.notify(Notifications.no_transactions_found())
        input("Press Enter to return to the menu.")
        return
    
    # Initialize the total spent to 0
    total_spent = Decimal("0.0")
    
    # Display the transactions with the converted amount
    for tx in transactions:
        transaction_date = tx["date"].strftime("%m-%d-%Y")
        converted_amount = Decimal(tx["amount"]) * conversion_rate

        total_spent += converted_amount

        print(
            f"| {transaction_date:<11} | "
            f"${converted_amount:>10,.2f} {chosen_currency:<4} | "
            f"{tx['category'].capitalize():<16} | "
            f"{tx['description'].capitalize():<18} |"
        )

    print("-" * 74)
    print(f"{'Total Spent:':<15} ${total_spent:>12,.2f} {chosen_currency}")
    print("-" * 74)
    input("\nPress Enter to return to the menu.")

# Generate a budget report showing all budgets in the chosen currency.
def generate_budget_report(cnxn):
    
    cursor = cnxn.cursor()
    budgets = get_budget(cursor)

    if not budgets:
        subject.notify(Notifications.no_budget_found())
        input("Press Enter to return to the menu.")
        return

    chosen_currency = validate_currency(cursor)
    conversion_rate = get_exchange_rate(cursor, chosen_currency)
    # If the conversion rate is not found, return to the menu
    if conversion_rate is None:
        subject.notify(Notifications.exchange_rate_not_found())
        input("Press Enter to return to the menu.")
        return

    print("\n" + "=" * 10 + " BUDGETS REPORT " + "=" * 10 + "\n")
    print("-" * 76)
    print("|" + f"Budget Report in {chosen_currency}".center(74) + "|")
    print("-" * 76)
    print(f"| {'Income':<15} | {'Expenses':<15} | {'Savings Goal':<18} | {'Remaining':<15} |")
    print("-" * 76)

    for b in budgets:
        income = b[1] * conversion_rate
        expenses = b[2] * conversion_rate
        savings = b[3] * conversion_rate
        remaining = b[4] * conversion_rate

        print( "| "
            f"${income:>10,.2f} {chosen_currency:<3} | "
            f"${expenses:>10,.2f} {chosen_currency:<3} | "
            f"${savings:>13,.2f} {chosen_currency:<3} | "
            f"${remaining:>10,.2f} {chosen_currency:<3} |"
        )

    print("-" * 76)
    input("\nPress Enter to return to the menu.")

# Generate a summary of savings goals in the chosen currency.
def generate_savings_goals_summary(cnxn, chosen_currency):
    
    cursor = cnxn.cursor()
    chosen_currency = validate_currency(cursor)
    
    conversion_rate = get_exchange_rate(cursor, chosen_currency)
    # If the conversion rate is not found, return to the menu
    if conversion_rate is None or conversion_rate == Decimal("1.0") and chosen_currency != BASE_CURRENCY:
        subject.notify(Notifications.exchange_rate_not_found())
        input("Press Enter to return to the menu.")
        return
    
    summary = get_savings_goals_summary(cursor)
    goals = get_goals(cursor)

    if not goals:
        subject.notify(Notifications.no_savings_goals())
        input("Press Enter to return to the menu.")
        return

    if not summary or summary["total_goals"] == 0:
        subject.notify(Notifications.no_savings_goals())

    else:
        print("\n" + "=" * 10 + " SAVING GOALS REPORT " + "=" * 10 + "\n")
        # Convert the summary values to the chosen currency
        total_target = Decimal(summary['total_target']) * conversion_rate
        total_progress = Decimal(summary['total_progress']) * conversion_rate
        overall_completion = f"{summary['overall_completion']:.2f}%"
        
        print(f"Saving Goals Summary".center(68))
        print("-" * 70)
        print(f"Total Goals Set:                {summary['total_goals']}")
        print(f"Total Target Amount:            ${total_target:,.2f} {chosen_currency}")
        print(f"Total Progress:                 ${total_progress:,.2f} {chosen_currency}")
        print(f"Overall Completion:             {overall_completion}\n")

        print("-" * 70)
        print(f"|" + "SAVING GOALS".center(68) +"|")
        print("-" * 70)
        print(f"| {'Goal Name':<15} | {'Target Amount':<17} | {'Progress':<15} | {'Completion':<10} |")
        print("-" * 70)

        for goal in goals:
            target_amount = Decimal(goal['target_amount']) * conversion_rate
            progress = Decimal(goal['current_progress']) * conversion_rate
            completion = f"{float(goal['completion_percentage']):.2f}%"
            print(f"| {goal['goal_name'].capitalize():<15} | "
                f"${target_amount:>12,.2f} {chosen_currency:<3} | "
                f"${progress:>10,.2f} {chosen_currency:<3} | "
                f"{completion:>10} |")
        print("-" * 70)

    input("\nPress Enter to return to the menu.")

# Saves the generated report into the Reports table in the database.
def save_report_to_database(cnxn, report_name, description, report_data):
    # Save the report to the database
    cursor = cnxn.cursor()
    unique_report_name = f"{report_name}"
    add_report(cursor, unique_report_name, description, report_data)
    cnxn.commit()
    notification = Notifications.report_saved(unique_report_name)
    subject.notify(notification)

# Fetch and display all saved reports from the database.
def view_saved_reports(cnxn):

    cursor = cnxn.cursor()
    reports = get_all_reports(cursor)
    
    # If there are no reports, notify the user and return
    if not reports:
        subject.notify(Notifications.no_reports_found())
        return
    
    # Limit the number of reports to display to 5
    max_reports = min(len(reports), 5)
    print("\n========== VIEW SAVED REPORTS ==========\n")
    print("-" * 70)
    print("|" + "SAVED REPORTS".center(68) + "|")
    print("-" * 70)
    print(f"| {'ID':<3} | {'Name':<40} | {'Created At':<17} |")
    print("-" * 70)

    for report in reports[:max_reports]:
        name = report['report_name']
        created_at = report['created_at'].strftime('%m-%d-%Y')
        print(f"| {report['id']:<3} | {name:<40} | {created_at:<17} |")

    print("-" * 70 + "\n")

    report_id = input("Enter the ID of the report you want to view (or back to return): ").strip()

    if report_id.lower() == 'back':
        return
    
    # Check if the input is a valid report ID
    if report_id.isdigit():
        # Fetch the detailed report by ID
        detailed_report = get_report_by_id(cursor, int(report_id))

        if detailed_report:
            print("\n" + "=" * 38)
            print("REPORT CONTENT".center(38))
            print("=" * 38 + "\n")
            print(detailed_report['report_data'])
            print("\n" + "=" * 38)
        else:
            subject.notify(Notifications.no_report_data_found())
    else:
        subject.notify(Notifications.invalid_choice())

    input("\nPress Enter to return to the menu.")

# Generates a general report and saves it to the database.

def generate_general_report(cnxn):
 
    cursor = cnxn.cursor()
    transactions = get_transactions(cnxn)
    budgets = get_budget(cursor)
    savings_summary = get_savings_goals_summary(cursor)

    # If there are no transactions, budgets, or savings goals, set the summary to 0
    if not savings_summary:
        savings_summary = {"total_goals": 0, "total_target": 0, "total_progress": 0, "overall_completion": 0}

    # Limit transactions and budgets to a maximum of 5
    transactions = transactions[:5]
    budgets = budgets[:5]

    report_data = (
        f"{'=' * 35}\n"
        f"{'GENERAL REPORT'.center(38)}\n"
        f"{'-' * 35}\n"
        f"Generated on: {datetime.now().strftime('%m-%d-%Y %H:%M:%S')}\n\n"
        f"{'-' * 35}\n"
        f"{'Transaction Summary'.center(38)}\n"
        f"{'-' * 35}\n"
        f"Total Transactions: {len(transactions)}\n\n"
        f"{'-' * 35}\n"
        f"{'Budget Summary'.center(38)}\n"
        f"{'-' * 35}\n"
        f"Total Budgets: {len(budgets)}\n\n"
        f"{'-' * 35}\n"
        f"{'Savings Goals Summary'.center(38)}\n"
        f"{'-' * 35}\n"
        f"Total Savings Goals: {savings_summary['total_goals']}\n"
        f"Total Target Amount: ${savings_summary['total_target']:,.2f} {BASE_CURRENCY}\n"
        f"Total Progress: ${savings_summary['total_progress']:,.2f} {BASE_CURRENCY}\n"
        f"Overall Completion: {savings_summary['overall_completion']:.2f}%\n"
        f"{'=' * 35}"
    )

    save_report_to_database(
        cnxn,
        report_name="General Report",
        description="A general overview of transactions, budgets, and savings goals.",
        report_data=report_data
    )

    print("\n" + "-" * 10 + " GENERAL REPORT " + "-" * 9 + "\n")
    print(report_data)
    input("\nPress Enter to return to the menu.")