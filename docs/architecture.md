# Inventory Replenishment POC Architecture

Status labels: **VERIFIED**, **PROPOSED**, **ASSUMPTION**, **UNKNOWN**.

## 1. Overview

**VERIFIED.** The POC is a same-origin web app: the browser loads a static HTML/CSS/JS dashboard from FastAPI; the dashboard calls JSON APIs; FastAPI queries PostgreSQL with psycopg using a read-only application role.

PostgreSQL is **ASSUMPTION** / provisional for this POC. **UNKNOWN:** RiteWay’s production database platform and architecture.

## 2. Architecture Flow

**VERIFIED** conceptual flow:

```
Browser
   ↓
HTML/CSS/JavaScript
   ↓
FastAPI
   ↓
Psycopg
   ↓
PostgreSQL
```

Dashboard URL (development): `http://127.0.0.1:8000/`.

## 3. Frontend

**VERIFIED** files:

- `frontend/index.html`
- `frontend/style.css`
- `frontend/app.js`

**VERIFIED** responsibilities:

- Presentation of API results (table, badges, summary counts)
- Client-side filtering by status (ALL / STOCKOUT / REORDER / OK) without a second database query
- Row selection and the explanation panel (Product, SKU, status reason sentence, API numeric fields, Decision)

The frontend **does not** recompute average demand, lead-time demand, reorder point, or status. Those values come from `GET /api/replenishment`. Display formatting (for example two decimal places) is presentation only.

FastAPI serves this folder with `StaticFiles` (`html=True`) mounted at `/` after the API routes.

## 4. Backend

**VERIFIED:**

- `backend/main.py`
- FastAPI application instance
- Endpoints:
  - `GET /api/health` — `{"status":"ok"}` (no database)
  - `GET /api/inventory` — `inventory_id`, `sku`, `location`, `on_hand`, `safety_stock`
  - `GET /api/replenishment` — one row per SKU in the current join result, including `average_daily_demand`, `lead_time_days`, `on_hand`, `safety_stock`, `lead_time_demand`, `reorder_point`, `status`

Replenishment math lives in SQL inside `/api/replenishment`, not in JavaScript.

## 5. Database

**VERIFIED:**

- Database name: `riteway_inventory_poc`
- Tables and relationships from `database/schema.sql`:

```
suppliers (supplier_id)
    ↑
products (sku, supplier_id → suppliers)
    ↑              ↑
inventory (sku)   sales (sku)
```

- `products.supplier_id` → `suppliers.supplier_id`
- `inventory.sku` → `products.sku`
- `sales.sku` → `products.sku`

There is no foreign key from inventory to sales. **ASSUMPTION:** POC grain is one inventory snapshot row per SKU and one sales row per SKU per date (`UNIQUE (sku, sale_date)`). **UNKNOWN:** RiteWay’s real schema.

## 6. Replenishment Data Flow

**VERIFIED:**

```
sales (observed units_sold)
   ↓
average observed sales  (AVG, exposed as average_daily_demand)
   ↓
lead-time demand        (× lead_time_days)
   ↓
reorder point           (+ safety_stock)
   ↓
status                  (STOCKOUT / REORDER / OK)
   ↓
FastAPI JSON
   ↓
dashboard
```

**ASSUMPTION:** observed sales stand in for demand in this POC.

## 7. Database Access

**VERIFIED:**

- Driver: **psycopg** (`dict_row` for JSON-friendly column names)
- Host: `127.0.0.1`
- Database: `riteway_inventory_poc`
- User: environment variable `DATABASE_USER`, default `riteway_app`
- Password: environment variable `DATABASE_PASSWORD` (not stored in source)

**ASSUMPTION / intent:** `riteway_app` is a dedicated **read-only** role. This document does not include any password.

## 8. Security / Operational Notes

**VERIFIED / ASSUMPTION (POC/dev only):**

- Credentials are not hard-coded in the repository; password comes from the environment
- Application role is intended to be read-only
- Database and app are local (`127.0.0.1`)
- This setup is a **development POC**, not a production deployment

**UNKNOWN:** production secrets management, network controls, and RiteWay security standards.

## 9. Known Limitations

**VERIFIED** limitations of the current POC:

- Synthetic data only; not RiteWay production data
- Three statuses only; no separate data-availability status (**RQ-05** not implemented)
- Inner join to `sales`: missing sales history would omit a product (**RQ-03** not implemented)
- Observed sales ≠ true demand; zero-sales days cannot be explained from the schema
- No authentication, no cloud, no ERP integration
- Safety stock and lead times are POC inputs, not confirmed RiteWay policy
- Local single-process FastAPI; no connection pooling documented as a requirement

Do not treat these as a production deployment checklist. **UNKNOWN:** what RiteWay would require in a live environment.
