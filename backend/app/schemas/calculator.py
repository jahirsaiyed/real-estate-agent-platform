"""Calculator schemas for UAE real estate financial tools."""
from __future__ import annotations

from pydantic import BaseModel, Field


class MortgageRequest(BaseModel):
    property_price_aed: float = Field(..., gt=0)
    down_payment_pct: float = Field(..., ge=0, le=100, description="Down payment as percentage")
    interest_rate: float = Field(..., gt=0, le=30, description="Annual interest rate %")
    term_years: int = Field(..., ge=1, le=25)
    nationality: str = Field(default="expat", description="'uae_national' or 'expat'")


class MortgageResponse(BaseModel):
    monthly_payment_aed: float
    total_interest_aed: float
    total_cost_aed: float
    loan_amount_aed: float
    down_payment_aed: float
    max_ltv_pct: float
    eligible: bool
    eligibility_note: str | None = None


class ROIRequest(BaseModel):
    purchase_price_aed: float = Field(..., gt=0)
    annual_rent_aed: float = Field(..., ge=0)
    service_charges_aed: float = Field(default=0, ge=0)
    management_fee_pct: float = Field(default=0, ge=0, le=100)


class ROIResponse(BaseModel):
    gross_yield_pct: float
    net_yield_pct: float
    annual_net_income_aed: float
    roi_5yr_pct: float
    roi_10yr_pct: float


class TCORequest(BaseModel):
    property_price_aed: float = Field(..., gt=0)
    mortgage_amount_aed: float = Field(default=0, ge=0)
    agent_commission_pct: float = Field(default=2.0, ge=0, le=10)


class TCOResponse(BaseModel):
    property_price_aed: float
    dld_fee_aed: float
    agent_commission_aed: float
    registration_trustee_fee_aed: float
    mortgage_processing_fee_aed: float
    dewa_connection_aed: float
    total_acquisition_cost_aed: float
    breakdown: dict[str, float]


class GoldenVisaRequest(BaseModel):
    property_price_aed: float = Field(..., gt=0)
    mortgage_amount_aed: float = Field(default=0, ge=0)
    nationality: str = Field(default="expat")


class GoldenVisaResponse(BaseModel):
    eligible: bool
    reason: str
    threshold_aed: float = 2_000_000
    equity_aed: float
    property_price_aed: float
