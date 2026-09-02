import os

import psycopg
from psycopg.rows import dict_row

import tests.conftest as conf

SIMULATION_SQL = """
WITH simulated_sales AS (
    SELECT sku, sale_date, units_sold
    FROM sales
    WHERE sku = '10001'
)
SELECT
    sku,
    product_name,
    sales_records,
    average_daily_demand,
    lead_time_demand,
    reorder_point,
    CASE
        WHEN sales_records = 0 THEN NULL
        WHEN on_hand = 0 THEN 'STOCKOUT'
        WHEN on_hand <= reorder_point THEN 'REORDER'
        ELSE 'OK'
    END AS status,
    CASE
        WHEN sales_records = 0 THEN 'Insufficient sales history'
        ELSE NULL
    END AS data_warning
FROM (
    SELECT
        p.sku,
        p.product_name,
        COUNT(sa.sku) AS sales_records,
        AVG(sa.units_sold) AS average_daily_demand,
        s.lead_time_days,
        i.on_hand,
        i.safety_stock,
        AVG(sa.units_sold) * s.lead_time_days AS lead_time_demand,
        AVG(sa.units_sold) * s.lead_time_days + i.safety_stock
            AS reorder_point
    FROM products AS p
    JOIN suppliers AS s ON p.supplier_id = s.supplier_id
    JOIN inventory AS i ON p.sku = i.sku
    LEFT JOIN simulated_sales AS sa ON p.sku = sa.sku
    WHERE p.sku IN ('10001', '10002')
    GROUP BY
        p.sku,
        p.product_name,
        s.lead_time_days,
        i.on_hand,
        i.safety_stock
) AS replenishment
ORDER BY sku
"""


@conf.requires_db
def test_rq06_zero_sales_history_simulation():
    conn = psycopg.connect(
        host="127.0.0.1",
        dbname="riteway_inventory_poc",
        user=os.environ.get("DATABASE_USER", "riteway_app"),
        password=os.environ["DATABASE_PASSWORD"],
        row_factory=dict_row,
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(SIMULATION_SQL)
            rows = {row["sku"]: row for row in cur.fetchall()}

    assert set(rows) == {"10001", "10002"}

    with_sales = rows["10001"]
    assert with_sales["sales_records"] == 30
    assert with_sales["average_daily_demand"] is not None
    assert with_sales["lead_time_demand"] is not None
    assert with_sales["reorder_point"] is not None
    assert with_sales["status"] in {"STOCKOUT", "REORDER", "OK"}
    assert with_sales["data_warning"] is None

    missing = rows["10002"]
    assert missing["sales_records"] == 0
    assert missing["average_daily_demand"] is None
    assert missing["lead_time_demand"] is None
    assert missing["reorder_point"] is None
    assert missing["status"] is None
    assert missing["data_warning"] == "Insufficient sales history"
