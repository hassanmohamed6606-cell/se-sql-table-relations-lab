
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("data.sqlite")

# STEP 1: Employees working in Boston
df_boston = pd.read_sql_query("""
    SELECT e.firstName, e.lastName
    FROM employees AS e
    INNER JOIN offices AS o
        ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston'
    ORDER BY e.firstName, e.lastName;
""", conn)

# STEP 2: Offices with zero employees
df_zero_emp = pd.read_sql_query("""
    SELECT o.officeCode, o.city
    FROM offices AS o
    LEFT JOIN employees AS e
        ON o.officeCode = e.officeCode
    WHERE e.employeeNumber IS NULL;
""", conn)

# STEP 3: All employees with their office city and state
df_employee = pd.read_sql_query("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees AS e
    LEFT JOIN offices AS o
        ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""", conn)

# STEP 4: Customers who have never placed an order
df_contacts = pd.read_sql_query("""
    SELECT
        c.contactFirstName,
        c.contactLastName,
        c.phone,
        c.salesRepEmployeeNumber
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName;
""", conn)

# STEP 5: Customer payments, sorted by amount descending
df_payment = pd.read_sql_query("""
    SELECT
        c.contactFirstName,
        c.contactLastName,
        p.amount,
        p.paymentDate
    FROM customers AS c
    INNER JOIN payments AS p
        ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC;
""", conn)

# STEP 6: Employees whose customers have an average credit limit over 90,000
df_credit = pd.read_sql_query("""
    SELECT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        COUNT(c.customerNumber) AS num_customers
    FROM employees AS e
    INNER JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(CAST(c.creditLimit AS REAL)) > 90000
    ORDER BY num_customers DESC;
""", conn)

# STEP 7: Number of orders and total units sold for each product
df_product_sold = pd.read_sql_query("""
    SELECT
        p.productName,
        COUNT(od.orderNumber) AS numorders,
        SUM(CAST(od.quantityOrdered AS INTEGER)) AS totalunits
    FROM products AS p
    INNER JOIN orderdetails AS od
        ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC;
""", conn)

# STEP 8: Number of distinct customers who purchased each product
df_total_customers = pd.read_sql_query("""
    SELECT
        p.productName,
        p.productCode,
        COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    INNER JOIN orderdetails AS od
        ON p.productCode = od.productCode
    INNER JOIN orders AS o
        ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC;
""", conn)

# STEP 9: Number of customers per office
df_customers = pd.read_sql_query("""
    SELECT
        COUNT(DISTINCT c.customerNumber) AS n_customers,
        o.officeCode,
        o.city
    FROM offices AS o
    INNER JOIN employees AS e
        ON o.officeCode = e.officeCode
    INNER JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode, o.city
    ORDER BY CAST(o.officeCode AS INTEGER);
""", conn)

# STEP 10: Employees who sold products purchased by fewer than 20 customers
df_under_20 = pd.read_sql_query("""
    SELECT DISTINCT
        e.employeeNumber,
        e.firstName,
        e.lastName,
        o.city,
        o.officeCode
    FROM employees AS e
    INNER JOIN offices AS o
        ON e.officeCode = o.officeCode
    WHERE e.employeeNumber IN (
        SELECT c.salesRepEmployeeNumber
        FROM customers AS c
        INNER JOIN orders AS ord
            ON c.customerNumber = ord.customerNumber
        INNER JOIN orderdetails AS od
            ON ord.orderNumber = od.orderNumber
        WHERE od.productCode IN (
            SELECT od2.productCode
            FROM orderdetails AS od2
            INNER JOIN orders AS ord2
                ON od2.orderNumber = ord2.orderNumber
            GROUP BY od2.productCode
            HAVING COUNT(DISTINCT ord2.customerNumber) < 20
        )
    )
    ORDER BY e.lastName, e.firstName;
""", conn)

# Close the database connection
conn.close()
