import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_index():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data == {"message":"Hello Arakis"}

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
        response_signup = await ac.post("/signup", json={
            "email": "test@test.com",
            "password": "12345678"
        })
        
        assert response_signup.status_code == 200
        response_login = await ac.post("/login", json={
            "email": "test@test.com",
            "password": "12345678"
        })

        assert response_login.status_code == 200

        check_protected_url = await ac.get("/protected")
        data = check_protected_url.json()
        assert data == {"data": "TOP SECRET"}

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