CREATE TABLE suppliers (
    supplier_id    TEXT    PRIMARY KEY,
    supplier_name  TEXT    NOT NULL,
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 0)
);

CREATE TABLE products (
    sku             TEXT PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    supplier_id     TEXT NOT NULL REFERENCES suppliers (supplier_id),
    unit_of_measure TEXT NOT NULL
);

CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY,
    sku          TEXT    NOT NULL REFERENCES products (sku),
    location     TEXT    NOT NULL,
    on_hand      INTEGER NOT NULL CHECK (on_hand >= 0),
    safety_stock INTEGER NOT NULL CHECK (safety_stock >= 0)
);

CREATE TABLE sales (
    sales_id    INTEGER PRIMARY KEY,
    sku         TEXT    NOT NULL REFERENCES products (sku),
    sale_date   DATE    NOT NULL,
    units_sold  INTEGER NOT NULL CHECK (units_sold >= 0),
    UNIQUE (sku, sale_date)
);
