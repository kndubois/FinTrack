### DATABASE HACKS ###

UPDATE TABLE table;
TRUNCATE TABLE table;
INSERT TABLE table;
DELETE TABLE table'
DROP TABLE table;
ALTER TABLE table DROP COLUMN table;


### Table Schema ###

-- Create Transactions table
CREATE TABLE Transactions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    date DATETIME NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category NVARCHAR(50) NOT NULL,
    description NVARCHAR(255)
);

-- Create Budget table
CREATE TABLE Budget (
    id INT IDENTITY(1,1) PRIMARY KEY,
    monthly_income DECIMAL(10, 2) NOT NULL,
    monthly_expenses DECIMAL(10, 2) NOT NULL,
    savings_goal DECIMAL(10, 2) NOT NULL,
    remaining_balance DECIMAL(10, 2) NOT NULL
);

-- Create SavingsGoals table
CREATE TABLE SavingsGoals (
    id INT IDENTITY(1,1) PRIMARY KEY,
    goal_name NVARCHAR(255) NOT NULL,
    target_amount DECIMAL(10, 2) NOT NULL,
    current_progress DECIMAL(10, 2) DEFAULT 0.00,
    completion_percentage DECIMAL(5, 2) DEFAULT 0.00,
    currency NVARCHAR(3) NOT NULL
);

-- Create Currency table
CREATE TABLE Currency (
    id INT IDENTITY(1,1) PRIMARY KEY,
    base_currency NVARCHAR(3) NOT NULL,
    chosen_currency NVARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(10, 4) NOT NULL,
    last_updated DATETIME DEFAULT GETDATE()
);

-- Create Reports table
CREATE TABLE Reports (
    id INT IDENTITY(1,1) PRIMARY KEY,
    report_name NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    description NVARCHAR(255),
    report_data NVARCHAR(MAX)
);