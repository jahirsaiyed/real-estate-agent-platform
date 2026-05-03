"""Tests for properties API and search."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_property_search_unauthenticated(client: AsyncClient) -> None:
    """Property search requires authentication."""
    resp = await client.get("/api/v1/properties/search")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_calculators_mortgage(client: AsyncClient) -> None:
    """Mortgage calculator returns correct structure."""
    resp = await client.post(
        "/api/v1/calculators/mortgage",
        json={
            "property_price_aed": 1_500_000,
            "down_payment_pct": 25,
            "interest_rate": 4.5,
            "term_years": 20,
            "nationality": "expat",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "monthly_payment_aed" in data
    assert "total_cost_aed" in data
    assert data["eligible"] is True
    assert data["monthly_payment_aed"] > 0


@pytest.mark.asyncio
async def test_calculators_mortgage_ltv_breach(client: AsyncClient) -> None:
    """Mortgage with > 75% LTV returns ineligible for expat."""
    resp = await client.post(
        "/api/v1/calculators/mortgage",
        json={
            "property_price_aed": 2_000_000,
            "down_payment_pct": 10,   # 90% LTV — exceeds 75% limit
            "interest_rate": 4.5,
            "term_years": 25,
            "nationality": "expat",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["eligible"] is False
    assert data["eligibility_note"] is not None


@pytest.mark.asyncio
async def test_calculators_roi(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/calculators/roi",
        json={
            "purchase_price_aed": 1_000_000,
            "annual_rent_aed": 60_000,
            "service_charges_aed": 10_000,
            "management_fee_pct": 5,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["gross_yield_pct"] == pytest.approx(6.0, rel=0.01)
    assert data["net_yield_pct"] < data["gross_yield_pct"]


@pytest.mark.asyncio
async def test_calculators_tco(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/calculators/tco",
        json={
            "property_price_aed": 2_000_000,
            "mortgage_amount_aed": 1_500_000,
            "agent_commission_pct": 2.0,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["dld_fee_aed"] == pytest.approx(80_000.0)
    assert data["total_acquisition_cost_aed"] > 2_000_000


@pytest.mark.asyncio
async def test_calculators_golden_visa_eligible(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/calculators/golden-visa",
        json={
            "property_price_aed": 3_000_000,
            "mortgage_amount_aed": 500_000,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["eligible"] is True
    assert data["equity_aed"] == pytest.approx(2_500_000.0)


@pytest.mark.asyncio
async def test_calculators_golden_visa_ineligible(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/calculators/golden-visa",
        json={
            "property_price_aed": 2_000_000,
            "mortgage_amount_aed": 1_200_000,  # equity = 800K < 2M threshold
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["eligible"] is False
