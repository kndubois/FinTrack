#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# budget.py
#
# This file contains the main menu for creating, 
# updating, and deleting budgets.
#
#################################################################

from database import (
    add_budget,
    get_budget_count,
    get_budget,
    delete_budget,
    update_budget,
    check_duplicate_budget,
    get_budget_by_id
)
from currency import validate_currency
from notifications import subject, Notifications

# Main menu for budgeting functionality
def budget_menu(cnxn):

    cursor = cnxn.cursor()
    chosen_currency = validate_currency(cursor)
    
    while True:

        print("\n" + "=" * 35 + "\n" + "BUDGET MENU".center(38) + "\n" + "=" * 35 + "\n")
        print("1. Create a New Budget")
        print("2. Overwrite a Budget")
        print("3. Delete a Budget")
        print("4. View Existing Budgets")
        print("5. Back to Main Menu\n")
        print("-" * 35)
        choice = input("Enter your choice: ").strip()
        print("-" * 35)
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            choice = int(choice)

            if choice == 1:
                if get_budget_count(cursor) >= 5:
                    subject.notify(Notifications.max_budgets_reached())
                    continue
                create_new_budget(cursor, cnxn, chosen_currency)
            elif choice == 2:
                overwrite_existing_budget(cursor, cnxn, chosen_currency)
            elif choice == 3:
                delete_existing_budget(cursor, cnxn, chosen_currency)
            elif choice == 4:
                display_budgets(cursor, chosen_currency)
            elif choice == 5:
                subject.notify(Notifications.returning_to_main_menu())
                break
        else:
            subject.notify(Notifications.invalid_choices_one_to_five())
            input("Press Enter to return to the main menu.\n")

# Create a new budget and notify the user of the budget creation.
def create_new_budget(cursor, cnxn, chosen_currency):

    while True:

        if get_budget_count(cursor) >= 5:
            print("\nYou already have 5 budgets. Please delete one before creating a new budget.")
            break
        
        print("\n======= Create a New Budget =======\n")
        
        # Get the budget details from the user
        budget_detials = get_budget_details(cursor, is_new=True)

        if not budget_detials:
            break
        
        # Unpack the budget details
        monthly_income, monthly_expenses, savings_goal, remaining_balance = budget_detials

        add_budget(cursor, monthly_income, monthly_expenses, savings_goal, remaining_balance)
        cnxn.commit()

        subject.notify(Notifications.budget_created(
            monthly_income,
            monthly_expenses,
            chosen_currency,
            savings_goal,
            remaining_balance
        ))

        while True:
            next_action = input("\nWould you like to create another budget? (yes/no): ").strip().lower()
            if next_action in ["yes", "y"]:
                break 
            elif next_action in ["no", "n"]:
                return  
            else:
                subject.notify(Notifications.invalid_yes_or_no())


    
# Display all existing budgets in a table format.
def display_budgets(cursor, chosen_currency):

    budgets = get_budget(cursor)

    if not budgets:
        subject.notify(Notifications.budget_not_found())
        return

    print("\n" + "=" * 10 + " Existing Budgets " + "=" * 10 + "\n")
    print("-" * 81)
    print(f"| {'ID':<1} | {'Income':<15} | {'Expenses':<15} | {'Savings Goal':<18} | {'Remaining':<15} |")
    print("-" * 81)

    for b in budgets:
        print(f"| {b.id:<2} | "
              f"${b.monthly_income:>10,.2f} {chosen_currency:<3} | "
              f"${b.monthly_expenses:>10,.2f} {chosen_currency:<3} | "
              f"${b.savings_goal:>13,.2f} {chosen_currency:<3} | "
              f"${b.remaining_balance:>10,.2f} {chosen_currency:<3} |")
    print("-" * 81)


# Overwrite an existing budget with new values.
def overwrite_existing_budget(cursor, cnxn, chosen_currency):
    
    budgets = get_budget(cursor)
    
    if not budgets:
        subject.notify(Notifications.budget_not_found())
        return
    
    display_budgets(cursor, chosen_currency)
    
    # Get the budget ID from the user and validate it
    while True:

        budget_id = input("\nEnter the ID of the budget to overwrite: ").strip()
        
        # Validate the budget ID
        if not budget_id.isdigit():
            subject.notify(Notifications.invalid_input())
            continue

        budget_id = int(budget_id)
        
        # Check if the budget ID exists
        if not get_budget_by_id(cursor, budget_id):
            subject.notify(Notifications.no_budget_id_found())
            continue

        print(f"\nOverwriting Budget ID {budget_id}.\n")
        
        budget_details = get_budget_details(cursor, is_new=False, budget_id=budget_id)
        if not budget_details:
            break

        monthly_income, monthly_expenses, savings_goal, remaining_balance = budget_details
                
        update_budget(cursor, budget_id, monthly_income, monthly_expenses, savings_goal, remaining_balance)
        cnxn.commit()
                
        subject.notify(Notifications.budget_overwritten(budget_id, monthly_income, monthly_expenses, savings_goal, remaining_balance))

        while True:
            next_action = input("Do you want to overwrite another budget? (yes/no): ").strip().lower()
            if next_action in ["yes", "y"]:
                break  # Continue the loop to ask for another budget ID
            elif next_action in ["no", "n"]:
                return  # Exit the function and return to the menu
            else:
                subject.notify(Notifications.invalid_yes_or_no())
                

# Get the budget details from the user and validate them.
def get_budget_details(cursor, is_new=True, budget_id=None):

    while True:

        if is_new:
            print("Enter the budget details:")
            print("-" * 35)
            income_prompt = ("Monthly Income:       $")
            expenses_prompt = ("Monthly Expenses:     $")
            savings_prompt = ("Savings Goal:         $")
        else:
            print("Enter the new budget details:")
            print("-" * 35)
            income_prompt = ("New Monthly Income:      $")
            expenses_prompt = ("New Monthly Expenses:    $")
            savings_prompt = ("New Savings goal:        $")

        monthly_income = get_numeric_input(income_prompt, Notifications.invalid_input())
        monthly_expenses = get_numeric_input(expenses_prompt, Notifications.invalid_expenses())
        savings_goal = get_numeric_input(savings_prompt, Notifications.invalid_savings_numeric())

        # Calculate the remaining balance
        remaining_balance = monthly_income - (monthly_expenses + savings_goal)

        # Validate the remaining balance
        if remaining_balance < 0:
            subject.notify(Notifications.error_budget_exceeds_income())
            while True:
                retry = input("Do you want to try again? (yes/no): ").strip().lower()
                if retry in ["yes", "y"]:
                    break
                elif retry not in ["no", "n"]:
                    return None
                else:
                    subject.notify(Notifications.invalid_yes_or_no())
                continue
            continue

        if check_duplicate_budget(cursor, monthly_income, monthly_expenses, savings_goal, None if is_new else budget_id):
            subject.notify(Notifications.duplicate_budget())

            while True:
                retry = input("Do you still want to proceed? (yes/no): ").strip().lower()
                if retry in ["yes", "y"]:
                    break
                elif retry in ["no", "n"]:
                    return None
                else:
                    subject.notify(Notifications.invalid_yes_or_no())
                    continue
            continue

        return monthly_income, monthly_expenses, savings_goal, remaining_balance


# Delete a budget by ID and show remaining budgets or handle no budgets left.

def delete_existing_budget(cursor, cnxn, chosen_currency):

    while True:

        budgets = get_budget(cursor)
        
        if not budgets:
            subject.notify(Notifications.budget_not_found())
            break  # Exit if no budgets remain

        print("\n" + "=" * 10 + " Deleting Budgets " + "=" * 10 + "\n")
        print("-" * 81)
        print(f"| {'ID':<1} | {'Income':<15} | {'Expenses':<15} | {'Savings Goal':<18} | {'Remaining':<15} |")
        print("-" * 81)
    
        for b in budgets[:5]:
            print(f"| {b.id:<2} | ${b.monthly_income:>10,.2f} {chosen_currency:<3} | "
                  f"${b.monthly_expenses:>10,.2f} {chosen_currency:<3} | "
                  f"${b.savings_goal:>13,.2f} {chosen_currency:<3} | "
                  f"${b.remaining_balance:>10,.2f} {chosen_currency:<3} |")
        print("-" * 81)
        
        budget_id = input("\nEnter the ID of the budget to delete: ").strip()
        
        # Validate the budget ID
        if budget_id.isdigit():
            budget_id = int(budget_id)
            if get_budget_by_id(cursor, budget_id):
                delete_budget(cursor, budget_id)
                cnxn.commit()
                subject.notify(Notifications.budget_id_deleted(budget_id))

            else:
                subject.notify(Notifications.no_budget_id_found())
                continue
        else:
            subject.notify(Notifications.invalid_input())

            continue

        budgets = get_budget(cursor)

        if not budgets:
            subject.notify(Notifications.no_remaining_budgets())
            break # Exit if no budgets remain
        
        while True:
            next_action = input("\nDo you want to delete another budget? (yes/no): ").strip().lower()
            if next_action in ["yes", "y"]:
                break  # Continue the loop to delete another budget
            elif next_action in ["no", "n"]:
                print("\nReturning to the Budget Menu.")
                return  # Exit the function
            else:
                subject.notify(Notifications.invalid_yes_or_no())

# Get numeric input from the user and validate it.
def get_numeric_input(prompt, error_message):
    while True:
        input_value = input(prompt).strip()
        if input_value.replace('.', '', 1).isdigit():
            return float(input_value) # Return the input value as a float
        else:
            print(error_message['text']) # Print the error message