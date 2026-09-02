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

**VERIFIED** current application SQL: `GET /api/replenishment` joins `products` to `sales` with a plain `JOIN` (inner join). In the **current** synthetic set, every product has sales, so no SKU is dropped for this reason today.

**PROPOSED** requirement area (see RQ-03 in `docs/requirements.md`): a product should not silently disappear from analysis only because sales history is missing. This is a **POC analysis conclusion**, **not** a confirmed RiteWay production requirement. **NOT IMPLEMENTED** as a LEFT JOIN / DATA ISSUE path in the running API.

## 7. Audit Conclusion

**VERIFIED:** the synthetic dataset is **structurally clean** for the current POC (counts, keys, non-negatives, no NULLs in the checked fields, full 30-day sales coverage per SKU).

**VERIFIED limitation:** demand **interpretation** is constrained: observed sales are a proxy; zero-sales days are unexplained by the schema; missing-sales behavior of an inner join is a completeness risk if such products appear later.

**ASSUMPTION:** “clean for the POC” does not mean “valid as RiteWay production data.”
