POSTGRESQL / PSQL CHEAT SHEET — RITEWAY INVENTORY POC
=========================================================

Project:
~/Projects/riteway-inventory-poc

Database:
riteway_inventory_poc

1. START / EXIT A POSTGRESQL SESSION
------------------------------------

Start as PostgreSQL admin:
sudo -u postgres psql -d riteway_inventory_poc

Exit PostgreSQL:
\q

Show databases:
\l

Show tables:
\dt

Describe a table:
\d products
\d inventory
\d suppliers
\d sales

Show PostgreSQL roles:
\du

Show current user:
SELECT current_user;

Show current database:
SELECT current_database();


2. PSQL / TERMINAL CONTROLS
---------------------------

If output opens in the pager:
q

Clear terminal:
Ctrl + L

Cancel an unfinished SQL command:
Ctrl + C

Important:
Ctrl + C inside psql cancels the current SQL input/query.
It does not exit PostgreSQL.


3. BASIC SQL
------------

Select everything:
SELECT * FROM products;

Select specific columns:
SELECT sku, product_name
FROM products;

Filter:
SELECT *
FROM inventory
WHERE on_hand = 0;

Sort ascending:
ORDER BY on_hand;

Sort descending:
ORDER BY on_hand DESC;

Count rows:
SELECT COUNT(*) FROM products;

Sum:
SELECT SUM(units_sold)
FROM sales;

Average:
SELECT AVG(units_sold)
FROM sales;

Round an average:
SELECT ROUND(AVG(units_sold), 2)
FROM sales;


4. GROUP BY
------------

GROUP BY means:
"Give me one result for each ..."

Example:
SELECT
    sku,
    AVG(units_sold)
FROM sales
GROUP BY sku;

For this POC:
GROUP BY sku
= calculate something separately for each product.


5. JOINS
--------

INNER JOIN:
SELECT ...
FROM products p
JOIN sales s
    ON p.sku = s.sku;

Meaning:
Only return rows where both sides have a match.

LEFT JOIN:
SELECT ...
FROM products p
LEFT JOIN sales s
    ON p.sku = s.sku;

Meaning:
Return every product, even if no matching sales record exists.

Important POC lesson:
INNER JOIN can hide missing sales history.
LEFT JOIN can expose missing sales history.


6. NULL
-------

NULL means the value is missing/unknown.

Correct:
WHERE column_name IS NULL;

Correct:
WHERE column_name IS NOT NULL;

Do NOT use:
WHERE column_name = NULL;


7. POC DATA CHECKS
------------------

Count core tables:
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM suppliers;
SELECT COUNT(*) FROM inventory;
SELECT COUNT(*) FROM sales;

Expected:
products   = 30
suppliers  = 6
inventory  = 30
sales      = 900

Zero observed-sales days:
SELECT
    sku,
    COUNT(*) FILTER (WHERE units_sold = 0) AS zero_sales_days,
    COUNT(*) AS total_sales_days
FROM sales
GROUP BY sku
ORDER BY zero_sales_days DESC, sku;

Negative sales:
SELECT *
FROM sales
WHERE units_sold < 0;

Negative inventory / safety stock:
SELECT *
FROM inventory
WHERE on_hand < 0
   OR safety_stock < 0;

Products without sales:
SELECT
    p.sku,
    p.product_name
FROM products p
LEFT JOIN sales s
    ON p.sku = s.sku
WHERE s.sku IS NULL;

Inventory without a matching product:
SELECT
    i.sku,
    i.location
FROM inventory i
LEFT JOIN products p
    ON i.sku = p.sku
WHERE p.sku IS NULL;

Sales without a matching product:
SELECT
    s.sku,
    s.sale_date
FROM sales s
LEFT JOIN products p
    ON s.sku = p.sku
WHERE p.sku IS NULL;


8. CURRENT REPLENISHMENT LOGIC
------------------------------

Observed daily sales proxy:
average_daily_demand = AVG(units_sold)

Lead-time demand:
lead_time_demand =
average_daily_demand * lead_time_days

Reorder point:
reorder_point =
lead_time_demand + safety_stock

Status:
STOCKOUT when on_hand = 0
REORDER when on_hand <= reorder_point
OK otherwise

Important:
The POC uses observed sales as a demand proxy.
It is not a statistically validated demand forecast.


9. CURRENT DATABASE ACCOUNT
---------------------------

Application database:
riteway_inventory_poc

Application role:
riteway_app

The application role is read-only for the current POC.

Credentials should NOT be stored in source code.

Environment variables:
DATABASE_USER
DATABASE_PASSWORD


10. CURRENT FASTAPI ENDPOINTS
-----------------------------

GET /api/health
GET /api/inventory
GET /api/replenishment

Dashboard:
http://127.0.0.1:8000/

FastAPI docs:
http://127.0.0.1:8000/docs


11. CURRENT PROJECT CHECKPOINTS
-------------------------------

a50f442
Baseline inventory replenishment POC

31e9f2d
Add POC requirements and architecture docs

a4dd1ff
Document missing sales history requirement

Git rule:
Git operations are performed manually by the developer.
AI/Cursor must not execute Git operations.


12. BUSINESS-ANALYSIS HABIT
---------------------------

Before writing SQL, state the business question.

Example:
"Which products do not have sales history?"

Then translate it into SQL.

Useful mental model:
BUSINESS QUESTION
    ↓
DATA NEEDED
    ↓
SQL
    ↓
RESULT
    ↓
BUSINESS INTERPRETATION

Do not assume that technically valid data is automatically
business-meaningful.


13. CURRENT POC DATA-QUALITY FINDINGS
-------------------------------------

The synthetic dataset is structurally clean.

Verified:
- 30 products
- 6 suppliers
- 30 inventory records
- 900 sales records
- 30 sales records for every SKU
- no orphan product/sales relationships
- no orphan inventory/product relationships
- no negative sales
- no negative inventory/safety stock
- no NULLs in required fields

Zero observed-sales periods:
- SKU 10026: 4 days
- SKU 10030: 5 days

These zeroes are NOT automatically classified as errors or stockouts.
The current data does not establish why those zeroes occurred.


14. CURRENT RQ-06 BEHAVIOR (POC)
--------------------------------

Implemented in this POC (not a RiteWay production rule):

A product with zero matching sales records remains visible in
replenishment analysis.

The system does not:
- fabricate a demand value
- silently omit the product
- treat insufficient history as a fourth inventory status

Normal inventory decisions (when matching sales records > 0):
STOCKOUT
REORDER
OK
data_warning = null

Insufficient sales history (COUNT of matching sales rows = 0):
average_daily_demand, lead_time_demand, reorder_point, status = null
data_warning = "Insufficient sales history"

data_warning is a separate data-quality / assessment field.
It is not an inventory status.

A day with units_sold = 0 is not insufficient history.


15. SAFE WORKING PRACTICE
-------------------------

Before changing data:
- prefer read-only queries
- use controlled simulations where possible
- avoid modifying the clean baseline dataset for tests

Before changing application code:
- identify the business requirement
- verify the current behavior
- make the smallest appropriate change
- test
- review
- commit a checkpoint manually
