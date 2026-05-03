"""UAE Real Estate Calculators — mortgage, ROI, TCO, Golden Visa."""
from __future__ import annotations

import math

from fastapi import APIRouter

from app.schemas.calculator import (
    GoldenVisaRequest,
    GoldenVisaResponse,
    MortgageRequest,
    MortgageResponse,
    ROIRequest,
    ROIResponse,
    TCORequest,
    TCOResponse,
)

router = APIRouter(prefix="/calculators", tags=["calculators"])

# UAE LTV limits (Central Bank regulations)
MAX_LTV_EXPAT_FIRST = 0.75       # 75% for expat, first property ≤ AED 5M
MAX_LTV_UAE_NATIONAL_FIRST = 0.80  # 80% for UAE nationals
MAX_LTV_ABOVE_5M = 0.65          # 65% for properties > AED 5M
GOLDEN_VISA_THRESHOLD = 2_000_000  # AED


@router.post("/mortgage", response_model=MortgageResponse)
def calculate_mortgage(req: MortgageRequest) -> MortgageResponse:
    """UAE mortgage calculator following Central Bank LTV guidelines."""
    is_national = req.nationality.lower() in ("uae_national", "uae", "emirati")

    if req.property_price_aed > 5_000_000:
        max_ltv = MAX_LTV_ABOVE_5M
    elif is_national:
        max_ltv = MAX_LTV_UAE_NATIONAL_FIRST
    else:
        max_ltv = MAX_LTV_EXPAT_FIRST

    down_payment_aed = req.property_price_aed * (req.down_payment_pct / 100)
    loan_amount = req.property_price_aed - down_payment_aed
    max_loan = req.property_price_aed * max_ltv

    eligible = loan_amount <= max_loan
    eligibility_note = None
    if not eligible:
        required_down = req.property_price_aed * (1 - max_ltv)
        eligibility_note = (
            f"Maximum LTV is {int(max_ltv * 100)}% for this profile. "
            f"Minimum down payment required: AED {required_down:,.0f}"
        )
        loan_amount = max_loan  # Recalculate with max allowed loan

    # Monthly payment via standard annuity formula
    monthly_rate = (req.interest_rate / 100) / 12
    n_months = req.term_years * 12

    if monthly_rate == 0:
        monthly_payment = loan_amount / n_months
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_months) / (
            (1 + monthly_rate) ** n_months - 1
        )

    total_repayment = monthly_payment * n_months
    total_interest = total_repayment - loan_amount

    return MortgageResponse(
        monthly_payment_aed=round(monthly_payment, 2),
        total_interest_aed=round(total_interest, 2),
        total_cost_aed=round(total_repayment + down_payment_aed, 2),
        loan_amount_aed=round(loan_amount, 2),
        down_payment_aed=round(down_payment_aed, 2),
        max_ltv_pct=round(max_ltv * 100, 1),
        eligible=eligible,
        eligibility_note=eligibility_note,
    )


@router.post("/roi", response_model=ROIResponse)
def calculate_roi(req: ROIRequest) -> ROIResponse:
    """Gross/net yield and ROI projections."""
    gross_yield = (req.annual_rent_aed / req.purchase_price_aed) * 100

    mgmt_fee = req.annual_rent_aed * (req.management_fee_pct / 100)
    annual_net = req.annual_rent_aed - req.service_charges_aed - mgmt_fee
    net_yield = (annual_net / req.purchase_price_aed) * 100

    # Simple ROI over 5/10 years (rent income only, no capital appreciation)
    roi_5yr = (annual_net * 5 / req.purchase_price_aed) * 100
    roi_10yr = (annual_net * 10 / req.purchase_price_aed) * 100

    return ROIResponse(
        gross_yield_pct=round(gross_yield, 2),
        net_yield_pct=round(net_yield, 2),
        annual_net_income_aed=round(annual_net, 2),
        roi_5yr_pct=round(roi_5yr, 2),
        roi_10yr_pct=round(roi_10yr, 2),
    )


@router.post("/tco", response_model=TCOResponse)
def calculate_tco(req: TCORequest) -> TCOResponse:
    """Total Cost of Ownership for Dubai property purchase."""
    price = req.property_price_aed

    # Dubai Land Department fee: 4% of property price
    dld_fee = price * 0.04

    # Agent commission (typically 2%)
    agent_fee = price * (req.agent_commission_pct / 100)

    # Registration trustee fee (Dubai property)
    registration_fee = 4000.0 if price >= 500_000 else 2000.0

    # Mortgage processing: 1% of loan + AED 2,500 (if mortgage)
    mortgage_fee = 0.0
    if req.mortgage_amount_aed > 0:
        mortgage_fee = req.mortgage_amount_aed * 0.01 + 2500

    # DEWA connection + misc
    dewa_fee = 2200.0

    total = price + dld_fee + agent_fee + registration_fee + mortgage_fee + dewa_fee

    return TCOResponse(
        property_price_aed=round(price, 2),
        dld_fee_aed=round(dld_fee, 2),
        agent_commission_aed=round(agent_fee, 2),
        registration_trustee_fee_aed=round(registration_fee, 2),
        mortgage_processing_fee_aed=round(mortgage_fee, 2),
        dewa_connection_aed=round(dewa_fee, 2),
        total_acquisition_cost_aed=round(total, 2),
        breakdown={
            "property_price": round(price, 2),
            "dld_fee_4pct": round(dld_fee, 2),
            "agent_commission": round(agent_fee, 2),
            "registration_trustee": round(registration_fee, 2),
            "mortgage_processing": round(mortgage_fee, 2),
            "dewa_connection": round(dewa_fee, 2),
        },
    )


@router.post("/golden-visa", response_model=GoldenVisaResponse)
def check_golden_visa(req: GoldenVisaRequest) -> GoldenVisaResponse:
    """UAE 10-year Golden Visa eligibility via property investment."""
    equity = req.property_price_aed - req.mortgage_amount_aed
    eligible = equity >= GOLDEN_VISA_THRESHOLD

    if eligible:
        reason = (
            f"Property equity of AED {equity:,.0f} meets the AED {GOLDEN_VISA_THRESHOLD:,.0f} "
            "minimum for the 10-year Golden Visa."
        )
    else:
        shortfall = GOLDEN_VISA_THRESHOLD - equity
        reason = (
            f"Property equity of AED {equity:,.0f} is AED {shortfall:,.0f} below the "
            f"AED {GOLDEN_VISA_THRESHOLD:,.0f} threshold. Reduce mortgage or increase property value."
        )

    return GoldenVisaResponse(
        eligible=eligible,
        reason=reason,
        threshold_aed=GOLDEN_VISA_THRESHOLD,
        equity_aed=round(equity, 2),
        property_price_aed=round(req.property_price_aed, 2),
    )
