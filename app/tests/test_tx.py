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
    create_tx(auth_client)

@pytest.mark.asyncio
async def test_get_all_txs(auth_client):
    await create_tx(auth_client)
    res = await auth_client.get("/transactions")
    data = res.json()
    assert data["transactions"][0]["type"] == "expense"
    assert data["transactions"][0]["amount"] == -25
    assert data["transactions"][0]["category"] == "grocery"
    assert data["transactions"][0]["place"] == "DELHAIZE"

@pytest.mark.asyncio
async def test_update_tx(auth_client):
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
    tx = data["transaction"]
    tx_id = int(tx["id"])
    
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
    print(tx)
