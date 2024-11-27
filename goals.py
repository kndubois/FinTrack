#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# goals.py
#
# This file contains the main menu for setting, 
# updating, deleting and viewing savings goals.
#
#################################################################

from decimal import Decimal
import datetime
from currency import validate_currency, get_exchange_rate
from database import (
    add_goal,
    get_goals,
    fetch_goals,
    update_goals,
    delete_goals,
    get_savings_goals_summary
)
from notifications import subject, Notifications


def goals_menu(cnxn):

    while True:

        print("\n" + "=" * 35 + "\n" + "SAVING GOALS MENU".center(38) + "\n" + "=" * 35 + "\n")
        print("1. Set a New Goal")
        print("2. Update a Goal")
        print("3. Delete a Goal")
        print("4. View All Goals")
        print("5. Back to Main Menu\n")
        print("-" * 35)
        choice = input("Enter your choice: ").strip()
        print("-" * 35)
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            choice = int(choice)

            if choice == 1:
                set_new_savings_goal(cnxn)
            elif choice == 2:
                update_goals_progress(cnxn)
            elif choice == 3:
                delete_goals_action(cnxn)
            elif choice == 4:
                view_all_savings_goals(cnxn)
            elif choice == 5:
                subject.notify(Notifications.returning_to_main_menu())
                break
        else:
            subject.notify(Notifications.invalid_choices_one_to_five())
            input("Press Enter to return to the Savings Goals menu.")

# Add a new savings goal
def set_new_savings_goal(cnxn):

    cursor = cnxn.cursor()
    chosen_currency = validate_currency(cursor)

    print("\n======= SET A NEW SAVINGS GOAL =======\n")

    while True:

        print("Enter the goal details:")
        print("-" * 35)

        goal_name = input("Goal Name:          ").strip()
        if not goal_name:
            subject.notify(Notifications.invalid_input()) 
            continue

        goal_name = handle_existing_goal(cursor, goal_name)
        break

    while True:
        target_amount = input("Target Amount:      $").strip()

        if not target_amount.replace('.', '', 1).isdigit():
            subject.notify(Notifications.invalid_input())
            continue

        target_amount = float(target_amount)
        break
    
    while True:
        starting_balance = input("Starting Balance:   $").strip()
    
        if not starting_balance:
            starting_balance = 0.0
        elif not starting_balance.replace('.', '', 1).isdigit():
            subject.notify(Notifications.invalid_input())
            continue

        starting_balance = float(starting_balance)
        break

    while True:
        chosen_currency = input("Currency:           ").strip().upper()
        if chosen_currency.isalpha():
            exchange_rate = get_exchange_rate(cursor, chosen_currency)
            if exchange_rate:
                break
            else:
                subject.notify(Notifications.exchange_rate_not_found(chosen_currency))
        else:
            subject.notify(Notifications.invalid_currency())
    
    while True:
        # Add the goal to the database
        if goal_name:
            add_goal(cursor, goal_name, target_amount, starting_balance, chosen_currency)
            cnxn.commit()
            subject.notify(Notifications.goal_created(goal_name, target_amount, starting_balance, chosen_currency))
            input("\nPress Enter to return to the Savings Goals menu.")
        else:
            subject.notify(Notifications.missing_goal_fields())
            input("\nPress Enter to continue.")
        break

# View all savings goals

def view_all_savings_goals(cnxn):

    print("\n===== VIEW ALL SAVINGS GOALS =====")
    
    cursor = cnxn.cursor()
    goals = get_goals(cursor)
    while True:
        if not goals:
            subject.notify(Notifications.no_savings_goals())
        else:
            print("\nCurrent savings goals:")
            print("-" * 35)
            for idx, goal in enumerate(goals, start=1):
                print(f"\n{idx}. {goal['goal_name'].capitalize()}")
                print(f"   - Target Amount:       ${float(goal['target_amount']):,.2f} {goal['currency']}")
                print(f"   - Current Progress:    ${float(goal['current_progress']):,.2f} {goal['currency']}")
                print(f"   - Completion:          {int(float(goal['completion_percentage']))}%")  

        break

# Update the progress on a savings goal
def update_goals_progress(cnxn):

    print("\n=== UPDATE PROGRESS ON SAVINGS GOAL ===\n")

    cursor = cnxn.cursor()
    goals = get_goals(cursor)

    if not goals:
        subject.notify(Notifications.no_savings_goals())
        return
    
    # 5 goals max
    print("Available Savings Goals:")
    print("-" * 35 + "\n")
    max_goals = min(len(goals), 5)
    for idx in range(max_goals):
        print(f"{idx + 1}. {goals[idx]['goal_name'].capitalize()}")
    
    # Select a goal to update
    while True:
        goal_choice = input(f"\nEnter the number of the goal to update progress (1 to {max_goals}): ").strip()
        if not goal_choice.isdigit() or int(goal_choice) not in range(1, max_goals + 1):
            print(f"Invalid selection. Please enter a number between 1 and {max_goals}.")
            continue

        selected_goal = goals[int(goal_choice) - 1]
        break
    
    # Update the goal progress
    remaining_amount = Decimal(selected_goal['target_amount']) - Decimal(selected_goal['current_progress'])
    print(f"\nYou have ${remaining_amount:,.2f} {selected_goal['currency']} remaining to reach your target.\n")
    
    # Add the amount to the goal
    while True:

        amount = input(f"Enter the amount to add to {selected_goal['goal_name']}: $").strip()
        if not amount.replace('.', '', 1).isdigit():
            subject.notify(Notifications.invalid_amount())
            continue

        amount = float(amount)
        new_current_progress = Decimal(selected_goal['current_progress']) + Decimal(amount)

        if new_current_progress > Decimal(selected_goal['target_amount']):
            print(f"\nError: Adding this amount would exceed the target amount of ${selected_goal['target_amount']:,.2f} {selected_goal['currency']}.")
            retry = input("Would you like to try again? (yes/no): ").strip().lower()
            if retry in ["n", "no"]:
                print("\nReturning to the Savings Goals menu.")
                return
            elif retry in ["y", "yes"]:
                continue
            else:
                subject.notify(Notifications.invalid_yes_or_no())
        else: # Update the goal progress
            completion_percentage = int((new_current_progress / Decimal(selected_goal['target_amount'])) * 100)
            update_goals(cursor, selected_goal['id'], new_current_progress)
            cnxn.commit()

            subject.notify(
                Notifications.goal_progress_updated(
                    selected_goal['goal_name'],
                    selected_goal['target_amount'],
                    selected_goal['currency'],
                    new_current_progress,
                    completion_percentage,
                )
            )

            # 50% progress
            if completion_percentage >= 50 and Decimal(selected_goal['current_progress']) < Decimal(selected_goal['target_amount']) / 2:
                subject.notify(Notifications.goal_halfway(selected_goal['goal_name']))

            # Notify about goal completion
            if completion_percentage == 100:
                subject.notify(Notifications.goal_completed(selected_goal['goal_name']))

            # Notify if the goal exceeds the target
            if new_current_progress > Decimal(selected_goal['target_amount']):
                subject.notify(Notifications.target_exceeded(selected_goal['goal_name']))

            input("\nPress Enter to return to the Savings Goals menu.")
            return

# Delete a savings goal
def delete_goals_action(cnxn):

    print("\n=== DELETE A SAVINGS GOAL ===")
    cursor = cnxn.cursor()
    goals = get_goals(cursor)

    if not goals:
        subject.notify(Notifications.no_savings_goals())
        return

    print("\nAvailable Goals:")
    print("-" * 35 + "\n")
    for idx, goal in enumerate(goals, start=1):
        print(f"{idx}. {goal['goal_name'].capitalize()}")
    
    # Select a goal to delete
    while True:
        print("\n" + "-" * 35)
        goal_choice = input(f"Enter the number of the goal to delete (1-{len(goals)}): ").strip()
        if goal_choice.isdigit() and 1 <= int(goal_choice) <= len(goals):
            selected_goal = goals[int(goal_choice) - 1]
            break
        print(f"Invalid selection. Please enter a number between 1 and {len(goals)}.")

        selected_goal = goals[int(goal_choice) - 1]
        break
    
    # Confirm the deletion
    confirmation = input(f"Are you sure you want to delete {selected_goal['goal_name']}? (yes/no): ").strip().lower()
    if confirmation in ["y", "yes"]:
        delete_goals(cursor, selected_goal['id'])
        cnxn.commit()
        subject.notify(Notifications.deleted_goal(selected_goal['goal_name']))
    elif confirmation in ["n", "no"]:
        subject.notify(Notifications.cancelled_goal(selected_goal['goal_name']))
    else:
        subject.notify(Notifications.invalid_yes_or_no())

# Handle existing goal names
def handle_existing_goal(cursor, goal_name):

    while True:
        existing_goal = fetch_goals(cursor, goal_name)
        if existing_goal:
            current_year = datetime.datetime.now().year
            suggested_name = f"{goal_name} {current_year}"
            
            subject.notify(Notifications.existing_goal(goal_name))
            print(f"Suggestion: {suggested_name.capitalize()}")
            
            suggestion = input("\nWould you like to modify the goal name to this suggestion? (yes/no): ").strip().lower()
            
            if suggestion in ['y', 'yes']:
                print("\nEnter the goal details:")
                print("-" * 35)
                return suggested_name
            elif suggestion in ['n', 'no']:
                goal_name = input("\nPlease enter a different goal name: ").strip()
                if not goal_name:
                    subject.notify(Notifications.empty_goal_name())
                continue
            else:
                subject.notify(Notifications.invalid_yes_or_no())
        else:
            return goal_name
