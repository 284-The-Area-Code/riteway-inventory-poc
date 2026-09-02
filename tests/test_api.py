import tests.conftest as conf


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@conf.requires_db
def test_inventory_shape(client):
    response = client.get("/api/inventory")
    assert response.status_code == 200
    rows = response.json()
    assert isinstance(rows, list)
    assert len(rows) == 30
    expected = {"inventory_id", "sku", "location", "on_hand", "safety_stock"}
    for row in rows:
        assert expected <= set(row.keys())


@conf.requires_db
def test_replenishment_clean_dataset(client):
    response = client.get("/api/replenishment")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 30

    allowed = {"STOCKOUT", "REORDER", "OK"}
    by_sku = {}
    for row in rows:
        assert row["status"] in allowed
        assert row["data_warning"] is None
        by_sku[str(row["sku"])] = row

    assert by_sku["10009"]["status"] == "STOCKOUT"
    assert by_sku["10026"]["status"] == "STOCKOUT"
