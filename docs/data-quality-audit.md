# Data Quality Audit

Status labels: **VERIFIED**, **PROPOSED**, **ASSUMPTION**, **UNKNOWN**.

## 1. Audit Purpose

**VERIFIED** purpose of this write-up: record a baseline data-quality audit of the **synthetic** POC dataset, to judge whether it is **structurally suitable** for the current replenishment analysis (joins, averages, reorder-point status).

This audit does **not** validate RiteWay production data. **ASSUMPTION:** results apply only to `riteway_inventory_poc` synthetic tables.

## 2. Dataset Counts

**VERIFIED:**

| Entity | Count |
|---|---|
| Products | 30 |
| Suppliers | 6 |
| Inventory records | 30 |
| Sales records | 900 |

## 3. Validation Checks

**VERIFIED** — checks performed and results. All listed checks **passed**.

| Check | Result |
|---|---|
| Sales coverage | Every SKU has 30 sales records |
| Products without sales records | 0 |
| Inventory records without matching products | 0 |
| Sales records without matching products | 0 |
| Negative sales values | 0 |
| Negative on-hand values | 0 |
| Negative safety-stock values | 0 |
| NULL supplier fields | 0 |
| NULL product fields | 0 |
| NULL inventory fields | 0 |
| NULL sales fields | 0 |

Referential integrity here means matching keys in the POC tables (`products.sku`, `inventory.sku`, `sales.sku`, `products.supplier_id` / `suppliers.supplier_id`) as exercised in this audit—not a claim about a production warehouse.

## 4. Zero Observed Sales

**VERIFIED** observations (not classified as errors by this audit):

- **SKU 10026:** 4 days with `units_sold = 0`
  - 2026-08-22
  - 2026-08-23
  - 2026-08-24
  - 2026-08-25
- **SKU 10030:** 5 days with `units_sold = 0`
  - 2026-07-31
  - 2026-08-01
  - 2026-08-02
  - 2026-08-03
  - 2026-08-04

**PROPOSED / interpretation:** zero observed sales on a day are **not** automatically a data error or a stockout. STOCKOUT in the POC is defined as `on_hand = 0`, which is a different fact.

## 5. Interpretation Limitation

**UNKNOWN / limitation of the data model:**

The current schema does **not** store historical product availability (or equivalent). Therefore this audit **cannot** determine whether a zero-sales period is:

- genuine zero demand,
- temporary product unavailability, or
- some other business condition.

No conclusion is drawn beyond that limitation.

## 6. SQL/Data Completeness Finding

**VERIFIED** systems-analysis experiment (controlled SQL):

- **`INNER JOIN sales`:** a product with **no** matching sales rows **disappears** from the replenishment result.
- **`LEFT JOIN sales`:** the product can **remain** visible; missing sales history can be seen instead of being dropped.

**VERIFIED** current application SQL: `GET /api/replenishment` uses a **LEFT JOIN** to `sales` and counts matching rows with `COUNT(sa.sku)`.

When `COUNT(sa.sku) = 0` (insufficient sales history for this POC):

- the product **remains** in the replenishment result
- `average_daily_demand`, `lead_time_demand`, `reorder_point`, and `status` are null
- `data_warning` is `"Insufficient sales history"`

When `COUNT(sa.sku) > 0`, existing formulas and STOCKOUT / REORDER / OK apply, and `data_warning` is null.

A day with `units_sold = 0` is **not** this case and is **not** automatically a data-quality error.

In the **current** synthetic set, every product has 30 sales records, so the zero-sales-history path is **not** visible in the live dashboard; it has been checked with read-only SQL simulation.

This LEFT JOIN / `data_warning` behavior implements **RQ-06** in this POC. It is **not** a confirmed RiteWay production requirement. A fourth inventory status (DATA ISSUE / UNABLE TO ASSESS) is **not** used.

## 7. Audit Conclusion

**VERIFIED:** the synthetic dataset is **structurally clean** for the current POC (counts, keys, non-negatives, no NULLs in the checked fields, full 30-day sales coverage per SKU).

**VERIFIED limitation:** demand **interpretation** is constrained: observed sales are a proxy; zero-sales days are unexplained by the schema. If a product had no sales rows, the API would retain it with null demand/status and `data_warning` rather than dropping it or fabricating demand `0`.

**ASSUMPTION:** “clean for the POC” does not mean “valid as RiteWay production data.”
