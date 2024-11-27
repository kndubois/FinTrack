#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# notifications.py
#
# This file contains the observer pattern 
# implementation for notifications.
#
#################################################################

class Observer:
    # Base class for all observers.
    
    context = None

    def update(self, message):
        raise NotImplementedError("The 'update' method must be implemented by subclasses.")

class Subject:
    # Subject class that maintains a list of observers and notifies them of updates.
    observers = []

    def attach(self, observer):
        if observer not in Subject.observers:
            Subject.observers.append(observer)

    def detach(self, observer):
        if observer in Subject.observers:
            Subject.observers.remove(observer)

    def notify(self, message):
        # Only notify observers matching the message context
        notified = False
        for observer in Subject.observers:
            if observer.context in message['contexts']:
                observer.update(message['text'])
                notified = True
        
        if not notified:
            GeneralObserver().update(message['text'])  # Fallback if no matching observer

# Concrete Observers

class GeneralObserver(Observer):
    # A general observer for fallback notifications
    context = "general"
    def update(self, message):
        print(f"{message}")

class TransactionObserver(Observer):
    context = "transaction"
    def update(self, message):
        print(f"\n-- Transaction Notification: {message}")

class BudgetObserver(Observer):
    context = "budget"
    def update(self, message):
        print(f"\n-- Budget Notification: {message}")

class SavingsGoalObserver(Observer):
    context = "savings_goal"
    def update(self, message):
        print(f"\n-- Savings Goal Notification: {message}")

class CurrencyObserver(Observer):
    # A currency observer for fallback notifications
    context = "currency"
    def update(self, message):
        print(f"\n-- Currency Notification: {message}")

subject = Subject()

# Centralized Notification Messages


class Notifications:

    #### GENERAL ####

    @staticmethod
    def welcome():
        return {"text": "=" * 35 + "\n" + "Welcome to FinTrack!".center(38) + "\n" + "=" * 35,
            "contexts": ["general"]}
    
    @staticmethod
    def goodbye():
        return {"text": "\nThank you for using FinTrack! Have a great day!", "contexts": ["general"]}
    
    
    @staticmethod
    def invalid_yes_or_no():
        return {"text": "\nERROR: Invalid input. Please enter yes or no.", "contexts": ["general"]}
    
    @staticmethod
    def invalid_choices_one_to_three():
        return {"text": "\nERROR: Invalid selection. Please enter a number from 1 to 3.\n", "contexts": ["general"]}
    
    @staticmethod
    def invalid_choices_one_to_five():
        return {"text": "\nERROR: Invalid choice. Please enter a number from 1 to 5.\n", "contexts": ["general"]}
    
    @staticmethod
    def invalid_choices_one_to_six():
        return {"text": "\nERROR: Invalid selection. Please enter a number from 1 to 6.\n", "contexts": ["general"]}
    
    @staticmethod
    def returning_to_main_menu():
        return {"text": "\nReturning to the main menu...\n", "contexts": ["general"]}
    
    @staticmethod
    def invalid_input():
        return {"text": "ERROR: Invalid input. Please enter a valid choice.", "contexts": ["general"]}
    
    @staticmethod
    def report_saved(report_name):
        return {
            "text": f"\n{report_name} has been generated successfully!",
            "contexts": ["general"]
        }
    
    @staticmethod
    def duplicate_report():
        return {"text": "\nERROR: Duplicate report. This report has already been saved.", "contexts": ["general"]}


    @staticmethod
    def invalid_choice():
        return "\nERROR: Invalid choice. Please try again."
    
    
    @staticmethod
    def invalid_option():
        return {"text": "ERROR: Invalid option. Please enter a valid choice.", "contexts": ["general"]}
    
    @staticmethod
    def invalid_amount():
        return {"text": "ERROR: Invalid amount entered. Please enter a valid numeric value."}
    
    @staticmethod
    def invalid_rate():
        return {"text": "ERROR: Invalid rate input. Please enter a numeric value.", "contexts": ["general"]}
    
    @staticmethod
    def invalid_input():
        return {"text": "ERROR: Invalid input. Please enter a numeric value.", "contexts": ["general"]}
    
    @staticmethod
    def invalid_choice():
        return {"text": "\nERROR: Invalid choice. Please enter a valid option.", "contexts": ["general"]}

    #### TRANSACTIONS ####

    @staticmethod
    def transaction_added(amount, currency, category, description):
        return f"Transaction added! [${amount:.2f} {currency}, Category: {category}, Description: {description}]"
        # A new transaction has been added! [Amount: $50.00 CAD, Category: Groceries]


    @staticmethod
    def no_reports_found():
        return {"text": "ERROR: No report found. Please generate a report first.", "contexts": ["transaction"]}


    @staticmethod
    def no_transactions_found():
        return {"text": "ERROR: No transactions found. Please log a transaction first.", "contexts": ["transaction"]}
    
    @staticmethod
    def invalid_transaction_date():
        return {"text": "ERROR: Invalid date format or value. Please enter the date as MM-DD-YYYY.\n", "contexts": ["transaction"]}
    

    @staticmethod
    def invalid_transaction_year():
        return {
            "text": "\nERROR: Invalid date format or value. Please ensure the year has 4 digits.\n", "contexts": ["transaction"]
        }
    
    @staticmethod
    def past_transaction_warning():
        return "WARNING: Past transaction detected. Confirm? (yes/no): "
    
    
    @staticmethod
    def invalid_future_transaction_date():
        return {"text": "ERROR: Transaction date cannot be beyond 2024. Please enter a valid date.", "contexts": ["transaction"]}
    
    @staticmethod
    def invalid_category():
        return {"text": "ERROR: 'Category' is a required field.", "contexts": ["transaction"]}
    
    @staticmethod
    def invalid_description():
        return {"text": "ERROR: 'Description' is a required field.", "contexts": ["transactionl"]}


    #### BUDGET ####

    @staticmethod
    def budget_overview(income, expenses, savings, remaining, currency):
        return f"Income: ${income:.2f} {currency}, Expenses: ${expenses:.2f} {currency}, Savings: ${savings:.2f} {currency}, Remaining: ${remaining:.2f} {currency}"
        # Income: $3000.00 CAD, Expenses: $1500.00 CAD, Savings: $500.00 CAD, Remaining: $1000.00 CAD"

    @staticmethod
    def budget_created(monthly_income, monthly_expenses, chosen_currency, savings_goal, remaining_balance):
        return {
            "text": (
                f"\nBudget Created Successfully!\n"
                f"{'-' * 35}\n" + "Budget Summary".center(38) + "\n" + 
                f"{'-' * 35}\n"
                f"Monthly Income:       ${monthly_income:,.2f} {chosen_currency}\n"
                f"Monthly Expenses:     ${monthly_expenses:,.2f} {chosen_currency}\n"
                f"Savings Goal:         ${savings_goal:,.2f} {chosen_currency}\n"
                f"Remaining Balance:    ${remaining_balance:,.2f} {chosen_currency}\n"
                f"{'-' * 35}"
            ),
            "contexts": ["budget"]
        }


    @staticmethod
    def invalid_numeric_value():
        return {"text": "\nERROR: Please enter a valid numeric value.", "contexts": ["budget"]}

    @staticmethod
    def budget_not_found():
        return {"text": "\nERROR: Budget not found. Please try again.", "contexts": ["budget"]}
    
    @staticmethod
    def no_budget_found():
        return {"text": "\nERROR: No budget found. Please create a budget first.\n", "contexts": ["budget"]}
    
    @staticmethod
    def no_budget_id_found():
        return {"text": "\nERROR: Budget ID not found. Please try again.", "contexts": ["budget"]}
    
    @staticmethod
    def budget_id_deleted(budget_id):
        return {
            "text": f"\nBudget ID {budget_id} deleted successfully.",
            "contexts": ["budget"]
        }
    
    @staticmethod
    def no_more_budgets():
        return {"text": "ERROR: No more budgets found. Please create a budget first.", "contexts": ["budget"]}
    
    @staticmethod
    def no_remaining_budgets():
        return {"text": "\nERROR: No remaining budgets found. Please create a budget first.", "contexts": ["budget"]}


    @staticmethod
    def max_budget_exceeded():
        return {"text": "ERROR: Maximum budget limit exceeded. Please adjust the values.", "contexts": ["budget"]}
    
    @staticmethod
    def max_budgets_reached():
        return {"text": "\nERROR: Maximum number (5) of budgets reached. Please delete or overwrite an existing budget first.", "contexts": ["budget"]}
        # You already have 5 budgets. Please delete or overwrite an existing one.

    @staticmethod
    def budget_overwritten(budget_id, monthly_income, monthly_expenses, savings_goal, remaining_balance):
        return {
            "text": (
                f"\nBudget Overwritten Successfully!\n"
                f"{'-' * 35}\n" + "Updated Budget Summary".center(36) + "\n" + 
                f"{'-' * 35}\n"
                f"ID:                      {budget_id}\n"
                f"Monthly Income:          ${monthly_income:,.2f}\n"
                f"Monthly Expenses:        ${monthly_expenses:,.2f}\n"
                f"Savings Goal:            ${savings_goal:,.2f}\n"
                f"Remaining Balance:       ${remaining_balance:,.2f}\n"
                f"{'-' * 35}\n"
            ),
            "contexts": ["budget"]
    }
    
    @staticmethod
    def budget_updated(budget_name, new_limit):
        return f"Budget '{budget_name}' has been updated. New Limit: ${new_limit:.2f}."
        # Budget for 'Entertainment' has been updated. New Limit: $500.00 CAD"
        # Budget updated. New Limit: $500.00 CAD"

    @staticmethod
    def error_budget_exceeds_income():
        return {"text": "\nERROR: Expenses and savings exceed income. Please adjust the values.", "contexts": ["budget"]}

    @staticmethod
    def duplicate_budget():
        return {"text": "\nERROR: A similar budget already exists. Please try a different budget.\n", "contexts": ["budget"]}

    '''
    @staticmethod
    def budget_created(income, currency, savings_goal):
        return {"text": f"Budget created! Income: ${income:.2f} {currency}, Savings Goal: ${savings_goal:.2f} {currency}.", "contexts": ["budget"]}
    '''

    @staticmethod
    def budget_exists():
        return {"text": "ERROR: A budget with the same name already exists. Please choose a different name.", "contexts": ["budget"]}
    
    @staticmethod
    def empty_budget_name():
        return {"text": "ERROR: Budget Name cannot be empty. Please enter a valid name.", "contexts": ["budget"]}
    
    @staticmethod
    def invalid_income():
        return {"text": "ERROR: Invalid input for income. Please enter a numeric value.", "contexts": ["budget"]}
    
    @staticmethod
    def invalid_expenses():
        return {"text": "ERROR: Invalid input for expenses. Please enter a numeric value.", "contexts": ["budget"]}

    #### GOALS ####

    @staticmethod
    def savings_goal_updated(goal_name, progress, currency):
        return {
            "text": f"Savings goal '{goal_name}' updated! Progress: ${progress:.2f} {currency}.",
            "contexts": ["savings_goal"]
        }

        # Progress updated for savings goal 'Vacation Fund'. Current Progress: $450.00 CAD
        # Savings goal 'Vacation Fund' progress updated. Current Progress: $450.00 CAD
        # A new savings goal 'Vacation Fund' has been created with a target of $1000.00 CAD"

    @staticmethod
    def goal_halfway(goal_name):
        return {"text": f"Congratulations! You've reached 50% of your target for the {goal_name} goal!", "contexts": ["savings_goal"]}

    @staticmethod
    def goal_completed(goal_name):
        return {"text": f"Success! You've reached 100% of your target for the {goal_name} goal!\nGoal Completed! Great job", "contexts": ["savings_goal"]}
        # Success! You've reached 100% of your target for the 'Vacation Fund' goal!\nGoal Completed! Great job on achieving your savings target.

    @staticmethod
    def target_exceeded(goal_name):
        return {"text": f"Congratulations! You've exceeded your target for the {goal_name} goal!", "contexts": ["savings_goal"]}

    

    
    
    @staticmethod
    def deleted_goal(goal_name):
        return {"text": f"\nSavings goal: {goal_name} has been deleted.", "contexts": ["savings_goal"]}
    
    @staticmethod
    def no_goals_found():
        return {"text": "ERROR: No goals found. Please create a goal first.", "contexts": ["savings_goal"]}
    
    @staticmethod
    def cancelled_goal(goal_name):
        return {"text": f"Deleting savings goal {goal_name} has been cancelled.", "contexts": ["savings_goal"]}
    
    @staticmethod
    def goal_not_found():
        return {"text": "ERROR: Goal not found. Please try again.", "contexts": ["savings_goal"]}
    
    def existing_goal(goal_name):
        return {
            "text": f"\nERROR: A goal named '{goal_name}' already exists.\n",
            "contexts": ["savings_goal"]
        }
        
    @staticmethod
    def empty_goal_name():
        return {"text": "\nERROR: Goal Name cannot be empty. Please enter a valid name.\n", "contexts": ["savings_goal"]}

    @staticmethod
    def invalid_savings_numeric():
        return {"text": "ERROR: Invalid input for amount. Please enter a numeric value.", "contexts": ["savings_goal"]}
    
    @staticmethod
    def no_savings_goals():
        return {"text": "\nERROR: No savings goals set yet. Please create a goal first.\n", "contexts": ["savings_goal"]}


    @staticmethod
    def goal_created(goal_name, target_amount, starting_balance, chosen_currency):
        return {
            "text": (
                f"\nNew Savings Goal Created Successfully!\n"
                f"{'-' * 35}\n" + "Goal Summary".center(38) + "\n" + 
                f"{'-' * 35}\n"
                f"Goal:               {goal_name.capitalize()}\n"
                f"Target Amount:      ${target_amount:,.2f} {chosen_currency}\n"
                f"Starting Balance:   ${starting_balance:,.2f} {chosen_currency}\n"
                f"{'-' * 35}"
            ),
            "contexts": ["savings_goal"]
        }

    @staticmethod
    def missing_goal_fields():
        return {"text": "ERROR: Both 'Goal Name' and 'Target Amount' are required. Please enter a valid name.", "contexts": ["savings_goal"]}
    
    @staticmethod
    def goal_progress_updated(goal_name, target_amount, currency, new_current_progress, completion_percentage):
        return {
            "text": (
                f"\nGoal Progress Updated!\n"
                f"{'-' * 35}\n" + "New Goal Summary".center(38) + "\n" + 
                f"{'-' * 35}\n"
                f"Goal:               {goal_name.capitalize()}\n"
                f"Target Amount:      ${target_amount:,.2f} {currency}\n"
                f"Starting Balance:   ${new_current_progress:,.2f} {currency}\n"
                f"Completion:         {completion_percentage}%\n"
                f"{'-' * 35}"
            ),
            "contexts": ["savings_goal"]
        }

    #### CURRENCY ####

    @staticmethod
    def invalid_currency():
        return {"text":  f"\nERROR: Invalid currency code or no exchange rate found.", "contexts": ["general"]} 
    
    
    '''
    @staticmethod
    def invalid_currency():
        return {"text": "ERROR: Invalid currency code. Please try again.", "contexts": ["general"]} 
    
        @staticmethod
    def invalid_currency_choice():
        return {"text": "Invalid input. Please choose 1, 2, 3.", "contexts": ["currency"]}
    '''
    
    
    @staticmethod
    def invalid_currency_rate():
        return {"text": "ERROR: Invalid currency rate input. Please enter a numeric value.", "contexts": ["currency"]}
    
    @staticmethod
    def conversion_failed():
        return {"text": "ERROR: Conversion failed. Please check the currency code.", "contexts": ["currency"]}
    
    @staticmethod
    def custom_rate():
        return {"text": "ERROR: Invalid currency rate input. Please enter a numeric value.", "contexts": ["currency"]}
    
    @staticmethod
    def exchange_rate_not_found(chosen_currency):
        return f"\nERROR: Exchange rate not found for {chosen_currency}."
    
    '''
    @staticmethod
    def exchange_rate_error():
        return f"Error fetching exchange rate. Status code: {response.status_code}"
    '''

    @staticmethod
    def exchange_rate_found():
        return {"text": "Exchange rate found!", "contexts": ["currency"]}   
    
    @staticmethod
    def exchange_rate_custom():
        return {"text": "Using custom exchange rate.", "contexts": ["currency"]}
    
    @staticmethod
    def exchange_rate_api():
        return {"text": "Using API exchange rate.", "contexts": ["currency"]}
    
    @staticmethod
    def updated_exchange_rate():
        return {"text": "\nExchange rate updated successfully.", "contexts": ["currency"]}
    
    @staticmethod
    def exchange_rate_greater():
        return {"text": "ERROR: Exchange rate must be greater than 0.", "contexts": ["currency"]}