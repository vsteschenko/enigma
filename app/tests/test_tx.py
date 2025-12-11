import pytest

@pytest.mark.asyncio
async def test_create_tx(auth_client):
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


@pytest.mark.asyncio
async def test_get_all_txs(auth_client):
    res = await auth_client.post("/transactions", json={
        "type": "expense",
        "amount": 25,
        "category": "grocery",
        "place": "DELHAIZE",
    })
    assert res.status_code == 201
    res = await auth_client.get("/transactions")
    data = res.json()
    assert data["transactions"][0]["type"] == "expense"
    assert data["transactions"][0]["amount"] == -25
    assert data["transactions"][0]["category"] == "grocery"
    assert data["transactions"][0]["place"] == "DELHAIZE"
    