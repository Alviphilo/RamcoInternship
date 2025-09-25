IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'SampleDB')
BEGIN
    CREATE DATABASE SampleDB;
END
GO

-- Switch to the DB
USE SampleDB;
GO

-- Create table only if it does not exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
BEGIN
    CREATE TABLE Users (
        UserID INT IDENTITY(1,1) PRIMARY KEY,
        FirstName VARCHAR(50) NOT NULL,
        LastName VARCHAR(50) NOT NULL,
        Email VARCHAR(100) UNIQUE NOT NULL,
        DateOfBirth DATE,
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
GO

-- Insert rows (safe, works in SQL Server)
INSERT INTO Users (FirstName, LastName, Email, DateOfBirth)
VALUES
 ('Alice', 'Johnson', 'alice.johnson@example.com', '1990-05-12'),
 ('Bob', 'Smith', 'bob.smith@example.com', '1985-09-23'),
 ('Charlie', 'Brown', 'charlie.brown@example.com', '2000-01-15');
GO

-- Select rows
SELECT * FROM Users;
GO
