import httpx
import pytest

pytestmark = pytest.mark.usefixtures("seeded_db")


@pytest.fixture
def auth_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key}


@pytest.mark.asyncio
async def test_get_organization_by_id(auth_headers, integration_app):
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/organizations/1", headers=auth_headers)
    assert response.status_code == 200
    organization = response.json()
    assert organization["id"] == 1
    assert "building" in organization
    assert "phones" in organization
    assert "activities" in organization


@pytest.mark.asyncio
async def test_get_organization_by_id_404(auth_headers, integration_app):
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/organizations/999999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_organizations_by_building(auth_headers, integration_app):
    building_id = 1
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/organizations/by-building/{building_id}", headers=auth_headers
        )
    assert response.status_code == 200
    organizations = response.json()
    assert isinstance(organizations, list)
    assert {organization["building"]["id"] for organization in organizations} == {
        building_id
    }


@pytest.mark.asyncio
async def test_organizations_by_activity(auth_headers, integration_app):
    activity_id = 3  # \"Молочная продукция\"
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/organizations/by-activity/{activity_id}", headers=auth_headers
        )
    assert response.status_code == 200
    organizations = response.json()
    assert isinstance(organizations, list)

    for organization in organizations:
        activity_ids = {activity["id"] for activity in organization["activities"]}
        assert activity_id in activity_ids


@pytest.mark.asyncio
async def test_organizations_by_activity_tree(auth_headers, integration_app):
    activity_id = 7  # \"Еда\"
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/organizations/by-activity-tree/{activity_id}", headers=auth_headers
        )
    assert response.status_code == 200
    organizations = response.json()
    assert isinstance(organizations, list)

    for organization in organizations:
        activity_ids = {activity["id"] for activity in organization["activities"]}
        assert activity_id in activity_ids


@pytest.mark.asyncio
async def test_search_by_name(auth_headers, integration_app):
    name = "Авто"
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/organizations/search", params={"name": name}, headers=auth_headers
        )
    assert response.status_code == 200
    organizations = response.json()
    assert organizations
    for organization in organizations:
        assert name.lower() in organization["name"].lower()


@pytest.mark.asyncio
async def test_in_radius_returns_orgs_near_point(auth_headers, integration_app):
    transport = httpx.ASGITransport(app=integration_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/organizations/in-radius",
            params={"lat": 55.751244, "lon": 37.618423, "radius": 1},
            headers=auth_headers,
        )
    assert response.status_code == 200
    organizations = response.json()
    assert isinstance(organizations, list)
    assert any(organization["building"]["id"] == 1 for organization in organizations)
