import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import psycopg
from psycopg.rows import dict_row

DATABASE_NAME = "riteway_inventory_poc"

app = FastAPI()


def get_connection():
    return psycopg.connect(
        host="127.0.0.1",
        dbname=DATABASE_NAME,
        user=os.environ.get("DATABASE_USER", "riteway_app"),
        password=os.environ["DATABASE_PASSWORD"],
        row_factory=dict_row,
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/inventory")
def list_inventory():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT inventory_id, sku, location, on_hand, safety_stock
                FROM inventory
                ORDER BY inventory_id
                """
            )
            return cur.fetchall()


@app.get("/api/replenishment")
def list_replenishment():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    sku,
                    product_name,
                    average_daily_demand,
                    lead_time_days,
                    on_hand,
                    safety_stock,
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
                    LEFT JOIN sales AS sa ON p.sku = sa.sku
                    GROUP BY
                        p.sku,
                        p.product_name,
                        s.lead_time_days,
                        i.on_hand,
                        i.safety_stock
                ) AS replenishment
                ORDER BY sku
                """
            )
            return cur.fetchall()


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)
