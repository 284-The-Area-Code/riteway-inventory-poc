# RiteWay Inventory Replenishment POC

A small proof-of-concept web application for **inventory replenishment decision support**.

The core question is:

> Given what we have, how fast we're using it, and how long replacement takes, which products need attention right now?

This project was built as a practical learning and demonstration exercise focused on SQL, relational database design, API development, deterministic business rules, data quality, and basic supply-chain/inventory concepts.

## Important context

This is a **POC, not a production inventory system**.

- The dataset is synthetic and does not represent RiteWay production data.
- The application is designed to demonstrate an approach, not replace an ERP or existing inventory platform.
- Business rules and assumptions are provisional unless confirmed by the appropriate business stakeholder.
- The replenishment decision is intentionally deterministic and explainable rather than based on opaque AI/ML forecasting.

## What the POC does

The application combines:

- product information
- supplier lead times
- current inventory
- safety stock
- observed daily sales

It then calculates:

**Average Daily Observed Sales**

`Average Daily Observed Sales = average observed units sold per day`

**Lead-Time Demand**

`Lead-Time Demand = Average Daily Observed Sales × Supplier Lead Time`

**Reorder Point**

`Reorder Point = Lead-Time Demand + Safety Stock`

The current decision statuses are:

- **STOCKOUT** — on-hand inventory is zero.
- **REORDER** — on-hand inventory is at or below the calculated reorder point.
- **OK** — on-hand inventory is above the calculated reorder point.

The POC also keeps data-quality limitations separate from the inventory decision. For example, when no sales records exist for a product, the application does not silently treat that as zero demand. Instead, the demand-related calculations remain unavailable and a separate warning is returned.

## Architecture

```text
Browser
   │
   ▼
HTML / CSS / JavaScript
   │
   ▼
FastAPI
   │
   ├── Python application logic
   └── SQL queries
   │
   ▼
PostgreSQL
   │
   ├── products
   ├── suppliers
   ├── inventory
   └── sales
```

## Technology

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **Database access:** psycopg
- **Testing:** pytest
- **Version control:** Git / GitHub

## Project structure

```text
riteway-inventory-poc/
├── backend/
│   └── main.py
├── data/
│   ├── inventory.csv
│   ├── products.csv
│   ├── README.txt
│   ├── sales.csv
│   └── suppliers.csv
├── database/
│   └── schema.sql
├── docs/
│   ├── architecture.md
│   ├── data-quality-audit.md
│   ├── postgres-cheatsheet.md
│   └── requirements.md
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_format_number.py
│   └── test_rq06_simulation.py
├── .cursor/
│   └── rules/
│       └── riteway-poc.mdc
├── .gitignore
├── requirements.txt
└── README.md
```

## Data model

The initial relational model contains four core tables:

### `suppliers`

Stores supplier identity and supplier lead time.

### `products`

Stores product identity and its relationship to a supplier.

### `inventory`

Stores on-hand quantity and safety stock by inventory record/location.

### `sales`

Stores observed sales by SKU and date.

The current POC assumes one sales record per SKU per day. The actual grain and business meaning of sales/consumption data would need to be confirmed before applying the approach to a production environment.

## Data-quality considerations

Data quality is treated as part of the decision-support problem rather than as an afterthought.

The POC explicitly considers issues such as:

- products with no matching sales history
- zero observed sales days
- stockouts
- orphaned relationships between tables
- negative or otherwise invalid quantities
- missing required values

A particularly important distinction is:

**0 observed sales is not automatically the same thing as 0 demand.**

A product can have zero observed sales because it genuinely had no demand, or because it was unavailable. Additional business data would be needed to distinguish those situations reliably.

## Requirements and documentation

Additional project documentation is available in `docs/`:

- `requirements.md` — requirement definitions and current implementation status
- `architecture.md` — application architecture and flow
- `data-quality-audit.md` — synthetic dataset quality checks and findings
- `postgres-cheatsheet.md` — PostgreSQL/psql reference used while building the POC

## Running the project

### 1. Create/activate the Python environment

The project uses a Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure database credentials

The application expects the database connection password in an environment variable.

For example, in zsh:

```zsh
export DATABASE_USER=riteway_app
read -s "DATABASE_PASSWORD?Database password: "
export DATABASE_PASSWORD
```

Do not commit credentials to Git.

### 4. Start the FastAPI application

From the project root:

```bash
.venv/bin/python -m uvicorn backend.main:app --reload
```

The application is available at:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/api/health
```

Replenishment endpoint:

```text
http://127.0.0.1:8000/api/replenishment
```

## Testing

Run the automated test suite with:

```bash
.venv/bin/pytest -v
```

The verified baseline currently consists of five passing tests. The test suite covers:

- health endpoint behavior
- inventory API response shape
- clean replenishment dataset behavior
- frontend number formatting for null/zero values
- the zero-sales-history data-quality simulation

## Current scope

The POC intentionally keeps its scope small.

It does **not** attempt to implement:

- ERP integration
- production deployment
- advanced demand forecasting
- machine learning models
- MRP
- ABC analysis
- EOQ optimization
- purchase-order automation

Those areas would require additional business requirements, validated data, and stakeholder confirmation before being added.

## Learning goals

This project is also being used as a practical learning exercise in:

- relational database design
- SQL joins and aggregation
- data-quality analysis
- REST API development
- backend/frontend integration
- deterministic business rules
- basic inventory and supply-chain concepts
- requirement tracing and technical documentation

## Status

**POC baseline verified.**

The current baseline has a functioning PostgreSQL-backed API, a browser dashboard, documented business rules, explicit handling for missing sales history, and an automated test suite.

