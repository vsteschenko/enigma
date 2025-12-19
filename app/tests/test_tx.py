import pytest

async def create_tx(auth_client):
    res = await auth_client.post("/transactions", json={
        "type": "expense",
        "amount": 25,
        "category": "grocery",
        "place": "DELHAIZE",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["message"] == "Transaction created"
    tx = data["transaction"]
    assert tx["amount"] == -25
    return tx

@pytest.mark.asyncio
async def test_create_tx(auth_client):
    await create_tx(auth_client)

@pytest.mark.asyncio
async def test_get_all_txs(auth_client):
    created = await create_tx(auth_client)

    res = await auth_client.get("/transactions")
    assert res.status_code == 200

    data = res.json()
    txs = data["transactions"]
    assert isinstance(txs, list)

    fetched = next((tx for tx in txs if tx["id"] == created["id"]), None)
    assert fetched is not None

    assert fetched["type"] == "expense"
    assert fetched["amount"] == -25
    assert fetched["category"] == "grocery"
    assert fetched["place"] == "DELHAIZE"

@pytest.mark.asyncio
async def test_update_tx(auth_client):
    tx = await create_tx(auth_client)
    assert tx["amount"] == -25
    tx_id = tx["id"]
    
    res = await auth_client.put(f"/transactions/{tx_id}", json={
        "type": "expense",
        "amount": 1,
        "category": "grocery",
        "place": "test",
    })
    assert res.status_code == 200
    upd_data = res.json()["transaction"]
    assert upd_data["id"] ==  tx_id
    assert upd_data["type"] == "expense"
    assert upd_data["category"] == "grocery"
    assert upd_data["amount"] == -1
    assert upd_data["place"] == "test"

@pytest.mark.asyncio
async def test_delete_tx(auth_client):
    tx = await create_tx(auth_client)
    tx_id = tx["id"]
    res = await auth_client.get("/transactions")
    data = res.json()
    before = data["transactions"]
    res = await auth_client.delete(f"/transactions/{tx_id}")
    assert res.status_code == 202
    res = await auth_client.get("/transactions")
    data = res.json()
    after = data["transactions"]
    assert len(before) == 1
    assert len(after) == 0
