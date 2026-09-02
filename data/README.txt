RiteWay Inventory Intelligence POC — Synthetic Dataset
===========================================================

These CSVs are entirely synthetic and are NOT RiteWay data.

Files
-----
suppliers.csv  : 6 synthetic suppliers and assumed lead times
products.csv   : 30 synthetic grocery SKUs
inventory.csv  : current inventory snapshot + POC safety-stock assumption
sales.csv      : 30 days of synthetic sales history (900 rows)

Purpose
-------
The dataset is designed to exercise Version 0.1 replenishment logic and
data-quality testing without using confidential company information.

Deliberate scenarios
--------------------
- Healthy inventory
- Below-reorder inventory
- Stockout
- High recent demand
- Long supplier lead time
- Periods of zero observed sales
- Stockout-distorted observed demand for SKU 10026

Important assumptions
---------------------
- Supplier names are fictional.
- Lead times are fictional.
- Safety stock is a POC assumption.
- Inventory locations are simplified.
- Sales are observed transactions, not direct measurements of true demand.
- Reorder-point logic must be validated against RiteWay's real processes/data
  before any production-facing use.
