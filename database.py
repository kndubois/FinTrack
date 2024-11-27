#################################################################
#
# 4SA3 Software Architecture Milestone #4
# 
# database.py
#
# This file contains the database operations for the application.
#
#################################################################

import pyodbc
from decimal import Decimal
from datetime import datetime
from notifications import subject, Notifications
import configparser

config = configparser.ConfigParser()
config.read("config.cfg")
connection_string = config["DATABASE"]["Connection_String"]

def create_connection():

    cnxn = pyodbc.connect(connection_string)
    
    if cnxn:
        return cnxn
    else:
        print("Error: Could not establish a connection to the database.")
        return None
    
def close_connection(cnxn):
    
    if cnxn:
        cnxn.close()

def setup_tables(cursor):

    tables = ["Transactions", "Budget", "SavingsGoals", "Currency", "Reports"]

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    cursor.execute('''
    CREATE TABLE Transactions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        date DATETIME NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        category NVARCHAR(50) NOT NULL,
        description NVARCHAR(255)
    )
    ''')

    cursor.execute('''
    CREATE TABLE Budget (
        id INT IDENTITY(1,1) PRIMARY KEY,
        monthly_income DECIMAL(10, 2) NOT NULL,
        monthly_expenses DECIMAL(10, 2) NOT NULL,
        savings_goal DECIMAL(10, 2) NOT NULL,
        remaining_balance DECIMAL(10, 2) NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE SavingsGoals (
        id INT IDENTITY(1,1) PRIMARY KEY,
        goal_name NVARCHAR(255) NOT NULL,
        target_amount DECIMAL(10, 2) NOT NULL,
        current_progress DECIMAL(10, 2) DEFAULT 0.00,
        completion_percentage DECIMAL(5, 2) DEFAULT 0.00,
        currency NVARCHAR(3) NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE Currency (
        id INT IDENTITY(1,1) PRIMARY KEY,
        base_currency NVARCHAR(3) NOT NULL,
        chosen_currency NVARCHAR(3) NOT NULL,
        exchange_rate DECIMAL(10, 4) NOT NULL,
        last_updated DATETIME DEFAULT GETDATE()
    )
    ''')

    cursor.execute('''
    CREATE TABLE Reports (
        id INT IDENTITY(1,1) PRIMARY KEY,
        report_name NVARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT GETDATE(),
        description NVARCHAR(255),
        report_data NVARCHAR(MAX)
    )
    ''')

# ---------------------------------
# CRUD Operations for Transactions
# ---------------------------------

def add_transaction(cursor, date, amount, category, description):

    cursor.execute('''
    INSERT INTO Transactions (date, amount, category, description)
    VALUES (?, ?, ?, ?)
    ''', (date, amount, category, description))

def get_transactions(cnxn):

    cursor = cnxn.cursor()
    cursor.execute('SELECT date, amount, category, description FROM Transactions')
    transactions = cursor.fetchall()
    cursor.close()
    return [
        {
            "date": tx[0],
            "amount": tx[1],
            "category": tx[2],
            "description": tx[3]
        } for tx in transactions
    ]

# ---------------------------------
# CRUD Operations for Budgets
# ---------------------------------

def add_budget(cursor, monthly_income, monthly_expenses, savings_goal, remaining_balance):
    cursor.execute('''
    INSERT INTO Budget (monthly_income, monthly_expenses, savings_goal, remaining_balance)
    VALUES (?, ?, ?, ?)
    ''', (monthly_income, monthly_expenses, savings_goal, remaining_balance))

def get_budget_count(cursor):
    cursor.execute('SELECT COUNT(*) FROM Budget')
    return cursor.fetchone()[0]

def get_budget(cursor):
    cursor.execute('SELECT id, monthly_income, monthly_expenses, savings_goal, remaining_balance FROM Budget')
    return cursor.fetchall()

def delete_budget(cursor, budget_id):
    cursor.execute('DELETE FROM Budget WHERE id = ?', (budget_id,))

def check_duplicate_budget(cursor, monthly_income, monthly_expenses, savings_goal, exclude_id=None):
    if exclude_id:
        cursor.execute('''
            SELECT * FROM Budget 
            WHERE monthly_income = ? AND monthly_expenses = ? AND savings_goal = ? AND id != ?
        ''', (monthly_income, monthly_expenses, savings_goal, exclude_id))
    else:
        cursor.execute('''
            SELECT * FROM Budget 
            WHERE monthly_income = ? AND monthly_expenses = ? AND savings_goal = ?
        ''', (monthly_income, monthly_expenses, savings_goal))
    
    return cursor.fetchone()


def update_budget(cursor, budget_id, monthly_income, monthly_expenses, savings_goal, remaining_balance):
    cursor.execute('''
        UPDATE Budget
        SET monthly_income = ?, 
            monthly_expenses = ?, 
            savings_goal = ?, 
            remaining_balance = ?
        WHERE id = ?
    ''', (monthly_income, monthly_expenses, savings_goal, remaining_balance, budget_id))


def get_budget_by_id(cursor, budget_id):
    cursor.execute('SELECT id, monthly_income, monthly_expenses, savings_goal, remaining_balance FROM Budget WHERE id = ?', (budget_id,))
    return cursor.fetchone()

# ---------------------------------
# CRUD Operations for Savings Goals
# ---------------------------------


def add_goal(cursor, goal_name, target_amount, current_progress=0.00, currency="CAD"):
    cursor.execute('''
    INSERT INTO SavingsGoals (goal_name, target_amount, current_progress, currency)
    VALUES (?, ?, ?, ?)
    ''', (goal_name, target_amount, current_progress, currency))

def get_goals(cursor):
    cursor.execute('SELECT id, goal_name, target_amount, current_progress, completion_percentage, currency FROM SavingsGoals')
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]



def fetch_goals(cursor, goal_name):
    cursor.execute('SELECT id, goal_name, target_amount, current_progress, currency FROM SavingsGoals WHERE LOWER(goal_name) = LOWER(?)', (goal_name,))
    return cursor.fetchone()

def update_goals(cursor, goal_id, new_progress):
    cursor.execute('''
        UPDATE SavingsGoals
        SET current_progress = ?
        WHERE id = ?
    ''', (new_progress, goal_id))

def delete_goals(cursor, goal_id):
    cursor.execute('DELETE FROM SavingsGoals WHERE id = ?', (goal_id,))

def get_savings_goals_summary(cursor):
    cursor.execute('''
        SELECT 
            COUNT(*) AS total_goals,
            SUM(target_amount) AS total_target,
            SUM(current_progress) AS total_progress,
            CASE 
                WHEN SUM(target_amount) > 0 
                THEN (SUM(current_progress) / SUM(target_amount)) * 100 
                ELSE 0 
            END AS overall_completion
        FROM SavingsGoals
    ''')
    result = cursor.fetchone()

    if result:
        return {
            "total_goals": result.total_goals,
            "total_target": result.total_target or 0,
            "total_progress": result.total_progress or 0,
            "overall_completion": result.overall_completion or 0
        }
    return None

# ---------------------------------
# CRUD Operations for Reports
# ---------------------------------

def add_report(cursor, report_name, description, report_data):
    cursor.execute('''
        INSERT INTO Reports (report_name, description, report_data)
        VALUES (?, ?, ?)
    ''', (report_name, description, report_data))

def get_all_reports(cursor):
    cursor.execute('SELECT id, report_name, created_at, description, report_data FROM Reports')
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_report_by_id(cursor, report_id):
    cursor.execute('SELECT id, report_name, created_at, description, report_data FROM Reports WHERE id = ?', (report_id,))
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def delete_report(cursor, report_id):
    cursor.execute('DELETE FROM Reports WHERE id = ?', (report_id,))

def is_duplicate_report(cursor, report_data):
    cursor.execute('SELECT COUNT(*) FROM Reports WHERE report_data = ?', (report_data,))
    return cursor.fetchone()[0] > 0

def save_report_to_database(cnxn, report_name, description, report_data):
    cursor = cnxn.cursor()

    if is_duplicate_report(cursor, report_data):
        subject.notify(Notifications.duplicate_report())
        return
    
    timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    unique_report_name = f"{report_name} ({timestamp})"

    add_report(cursor, unique_report_name, description, report_data)
    cnxn.commit()
    subject.notify(Notifications.report_saved(unique_report_name))


# ---------------------------------
# CRUD Operations for currency
# ---------------------------------

def fetch_all_exchange_rates(cursor, base_currency):
    cursor.execute('''
        SELECT chosen_currency, exchange_rate, last_updated
        FROM Currency 
        WHERE base_currency = ?
    ''', (base_currency,))
    rates = cursor.fetchall()
    return {row.chosen_currency: Decimal(row.exchange_rate) for row in rates}


def update_exchange_rate(cursor, base_currency, chosen_currency, exchange_rate, last_updated):
    cursor.execute('''
        MERGE INTO Currency AS target
        USING (SELECT ? AS base_currency, ? AS chosen_currency) AS source
        ON target.base_currency = source.base_currency AND target.chosen_currency = source.chosen_currency
        WHEN MATCHED THEN
            UPDATE SET exchange_rate = ?, last_updated = ?
        WHEN NOT MATCHED THEN
            INSERT (base_currency, chosen_currency, exchange_rate, last_updated)
            VALUES (?, ?, ?, ?);
    ''', (base_currency, chosen_currency, exchange_rate, last_updated,
          base_currency, chosen_currency, exchange_rate, last_updated))


def get_exchange_rate_from_db(cursor, base_currency, chosen_currency):
    
    cursor.execute('''
        SELECT exchange_rate 
        FROM Currency
        WHERE base_currency = ? AND chosen_currency = ?
    ''', (base_currency, chosen_currency))
    result = cursor.fetchone()
    if result:
        return Decimal(result[0]) 
    return None

###
# Database setup
###

cnxn = create_connection()
if cnxn:
    cursor = cnxn.cursor()
    setup_tables(cursor)
    cursor.close()
    cnxn.close()
