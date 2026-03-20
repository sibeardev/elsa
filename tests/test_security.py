import httpx
import pytest


@pytest.mark.asyncio
async def test_missing_api_key_returns_401(integration_app):
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/organizations/by-building/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_api_key_returns_401(integration_app):
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/organizations/by-building/1",
            headers={"X-API-Key": "wrong"},
        )
    assert response.status_code == 401
