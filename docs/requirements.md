# Inventory Replenishment POC Requirements

Status labels used in this document: **VERIFIED**, **PROPOSED**, **ASSUMPTION**, **UNKNOWN**, **NOT IMPLEMENTED**.

## 1. POC Purpose

**VERIFIED.** This project is a small Proof of Concept for an **Inventory Replenishment Decision-Support Web Application**. It demonstrates technical implementation, SQL/relational thinking, business analysis, data-quality awareness, and explainable deterministic rules using **synthetic** data.

It is **not** a production RiteWay system, an ERP replacement, a purchasing automation system, or an AI forecasting system.

## 2. Core Business Question

**VERIFIED** (stated objective of this POC):

> Given what we have, how fast we're using it, and how long replacement takes, which products need attention right now?

## 3. Scope

**VERIFIED** — currently in scope for this POC:

- Local PostgreSQL database `riteway_inventory_poc` with tables `suppliers`, `products`, `inventory`, and `sales`
- Synthetic dataset (6 suppliers, 30 products, 30 inventory rows, 900 sales rows)
- FastAPI backend with `GET /api/health`, `GET /api/inventory`, `GET /api/replenishment`
- HTML/CSS/JavaScript dashboard served at `http://127.0.0.1:8000/`
- Status counts (STOCKOUT, REORDER, OK), client-side status filters, row selection, an explanation panel that displays API fields, and a data-warning column (`data_warning`)
- Replenishment formulas and status rules implemented in SQL and verified in PostgreSQL

**VERIFIED** in this slice: RQ-01, RQ-02, and RQ-06 (see section 4). **PROPOSED** interpretation: RQ-04. Git history is maintained by the developer; a baseline commit message `Baseline inventory replenishment POC` (`a50f442`) was recorded by the project owner.

## 4. Functional Requirements

### Implemented / verified in this POC

| ID | Statement | Status |
|---|---|---|
| **RQ-01** | The system shall identify products requiring replenishment attention based on current on-hand inventory, observed sales, supplier lead time, and safety stock. | **VERIFIED** as implemented in this POC via `/api/replenishment` and the dashboard. **ASSUMPTION:** this is a POC rule set, not a confirmed RiteWay production policy. |
| **RQ-02** | The replenishment calculation shall use observed sales as the demand proxy for this POC. | **VERIFIED** as implemented (`AVG(units_sold)` aliased as `average_daily_demand`). This is **not** a statistically validated demand forecast. |
| **RQ-06** | The system should retain products with insufficient or missing sales history in replenishment analysis and should not fabricate a demand value or silently omit the product. The data limitation should be represented separately from the normal inventory decision. | **VERIFIED** as implemented in this POC via `/api/replenishment`. If `COUNT` of matching sales rows = 0, the product is retained; `average_daily_demand`, `lead_time_demand`, `reorder_point`, and `status` are null; `data_warning` is `"Insufficient sales history"`. If `COUNT` > 0, existing formulas and STOCKOUT / REORDER / OK apply and `data_warning` is null. This POC does **not** add `UNABLE TO ASSESS` (or any fourth value) as an inventory status. This is a POC rule, not a confirmed RiteWay production requirement. |

RQ-06 refines how RQ-03 and RQ-05 are represented: keep STOCKOUT, REORDER, and OK as the inventory decisions; do not treat insufficient sales history as a fourth inventory status.

### Proposed / not fully implemented

| ID | Statement | Status |
|---|---|---|
| **RQ-03** | The system shall not silently treat missing sales history as zero demand. | Overlap with **RQ-06** is **VERIFIED** as implemented in this POC: zero matching sales records do **not** become demand `0`. Broader thresholds (for example a minimum number of sales days) are **NOT IMPLEMENTED**. **ASSUMPTION:** not a confirmed RiteWay production policy. The live synthetic set still has 30 sales rows per SKU, so this path is not visible in the live dashboard. |
| **RQ-04** | Zero observed sales on a day shall not automatically be classified as a data error or stockout. | **PROPOSED** as a documentation/interpretation rule. **VERIFIED** that the current status rules do **not** treat a zero-sales *day* as STOCKOUT; STOCKOUT is `on_hand = 0` only. Zero-sales days are not flagged as data errors in the application. |
| **RQ-05** | The system shall distinguish data-availability limitations from the replenishment decision when sufficient information is unavailable. | Overlap with **RQ-06** is **VERIFIED** as implemented in this POC: `status` is null and `data_warning` is set when sales history is insufficient. A fourth inventory status (DATA ISSUE / UNABLE TO ASSESS) is **NOT IMPLEMENTED** (by design). Other kinds of missing inputs are **NOT IMPLEMENTED**. **ASSUMPTION:** not a confirmed RiteWay production policy. |

These remaining items are **not** confirmed RiteWay production requirements.

## 5. Data Requirements

**VERIFIED** — data currently used (from `database/schema.sql` and the synthetic CSVs). Column lists are the POC schema only.

### suppliers

| Column | Type / constraint (POC) |
|---|---|
| `supplier_id` | TEXT, primary key |
| `supplier_name` | TEXT, required |
| `lead_time_days` | INTEGER, required, `>= 0` |

### products

| Column | Type / constraint (POC) |
|---|---|
| `sku` | TEXT, primary key |
| `product_name` | TEXT, required |
| `category` | TEXT, required |
| `supplier_id` | TEXT, required, foreign key to `suppliers.supplier_id` |
| `unit_of_measure` | TEXT, required |

### inventory

| Column | Type / constraint (POC) |
|---|---|
| `inventory_id` | INTEGER, primary key |
| `sku` | TEXT, required, foreign key to `products.sku` |
| `location` | TEXT, required |
| `on_hand` | INTEGER, required, `>= 0` |
| `safety_stock` | INTEGER, required, `>= 0` |

### sales

| Column | Type / constraint (POC) |
|---|---|
| `sales_id` | INTEGER, primary key |
| `sku` | TEXT, required, foreign key to `products.sku` |
| `sale_date` | DATE, required |
| `units_sold` | INTEGER, required, `>= 0` |
| | UNIQUE (`sku`, `sale_date`) |

**ASSUMPTION:** one inventory row per SKU in the synthetic set; one sales row per SKU per day. **UNKNOWN:** whether this matches any RiteWay production grain.

## 6. Business Rules

**VERIFIED** in PostgreSQL and in `GET /api/replenishment`:

```
average_daily_demand = AVG(observed sales)   -- AVG(sa.units_sold)
lead_time_demand     = average_daily_demand × lead_time_days
reorder_point        = lead_time_demand + safety_stock
```

Status (when matching sales records > 0):

1. **STOCKOUT** when `on_hand = 0`
2. **REORDER** when `on_hand <= reorder_point`
3. **OK** otherwise

When matching sales records = 0: `average_daily_demand`, `lead_time_demand`, `reorder_point`, and `status` are null; `data_warning` is `"Insufficient sales history"`. A day with `units_sold = 0` is not this case.

Inventory decisions remain these three statuses. Missing or insufficient **sales history** is **not** a new inventory status (**RQ-06**).

The field name `average_daily_demand` is **observed sales**, not a forecast.

**ASSUMPTION:** these formulas and the three statuses are POC rules. **UNKNOWN:** RiteWay’s actual replenishment policy, safety-stock policy, and thresholds.

## 7. Data Interpretation Rules

**VERIFIED / ASSUMPTION (POC):**

- **Observed sales vs true demand:** Sales are recorded transactions (`units_sold`). They are used as a demand *proxy*. They are not a measurement of unconstrained true demand.
- **Zero observed sales on a day:** Present for SKU 10026 (4 days) and SKU 10030 (5 days). **PROPOSED (RQ-04):** these days are not automatically a data error or a stockout. **UNKNOWN:** whether each zero represents genuine zero demand, unavailability, or another condition. The schema has no availability history to decide.
- **Missing sales history:** **VERIFIED (RQ-06)** in this POC: do not silently treat missing history as zero demand; do not omit the product; do not fabricate demand. Represent the limitation as `data_warning` (`"Insufficient sales history"`) with null demand, reorder point, and status, separate from STOCKOUT / REORDER / OK. The current synthetic set has no such product; the path is verified with read-only SQL simulation.
- **Distinction:** **Missing or insufficient sales history** for calculating observed demand → `data_warning` (**RQ-06**). **An individual day with `units_sold = 0`** → not automatically a data-quality error (**RQ-04**).

Do not invent further interpretation rules.

## 8. Assumptions

**ASSUMPTION:**

- All application data used here is synthetic and fictional.
- Observed sales are the demand proxy for this POC.
- Business rules in section 6 are deterministic and encoded in SQL.
- Supplier names, lead times, safety stock, locations, and SKUs are POC values.
- Actual RiteWay production requirements, schema, and processes are not yet known.
- PostgreSQL, the table names, and the local stack are provisional for this POC.
- The application database role is intended to be read-only (`riteway_app` by default).
- Insufficient or missing sales history is a **data-quality / assessment condition** (`data_warning`), not a fourth inventory status.

## 9. Unknowns / Items Requiring Business Confirmation

**UNKNOWN** (do not fill these in without business input):

- RiteWay’s actual ERP / database structure and platform
- Actual inventory process and replenishment workflow
- Actual business thresholds (reorder, safety stock, lead time)
- How to treat stockout-distorted or constrained demand
- Actual data-quality rules and exception handling
- Meaning of zero-sales days
- Production architecture, security, and integration requirements
- Whether products may exist without sales history in real operations

## 10. Out of Scope

**VERIFIED** as out of scope for this POC (unless explicitly approved later):

- Replacing an ERP
- Automating purchasing or suggesting order quantities
- AI/ML or statistical forecasting models
- Production integration with RiteWay systems
- Authentication, cloud deployment, Docker, or invented RiteWay workflows
- Expanding RQ-03 / RQ-05 beyond the RQ-06 contract (minimum-day thresholds, other missing inputs, or a fourth inventory status) unless explicitly approved
