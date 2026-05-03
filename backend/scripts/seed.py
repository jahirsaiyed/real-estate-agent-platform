"""Seed script: creates default tenant, admin user, and sample properties.

Run: python -m scripts.seed
"""
from __future__ import annotations

import asyncio
import os
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://rea_user:rea_password@localhost:5432/realestateagent",
)


async def seed() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        async with db.begin():
            await _seed_tenant_and_admin(db)
            await _seed_properties(db)

    await engine.dispose()
    print("Seed complete.")


async def _seed_tenant_and_admin(db: AsyncSession) -> None:
    from sqlalchemy import select
    from app.models.tenant import Tenant
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    # Check if already seeded
    existing = (await db.execute(select(Tenant).where(Tenant.slug == "sceptre-estate"))).scalar_one_or_none()
    if existing:
        print("Tenant already exists — skipping tenant/user seed.")
        return

    tenant = Tenant(
        id=uuid.uuid4(),
        name="Sceptre Estate",
        slug="sceptre-estate",
        plan="enterprise",
        settings={
            "persona_name": "Layla",
            "tone": "warm_professional",
            "rera_number": "REA-12345",
            "languages": ["en", "ar", "hi", "ru"],
        },
        is_active=True,
    )
    db.add(tenant)
    await db.flush()

    admin = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email="admin@sceptreestate.com",
        full_name="Platform Admin",
        hashed_password=hash_password("Admin@12345!"),
        role=UserRole.tenant_admin,
        is_active=True,
    )
    db.add(admin)
    await db.flush()

    print(f"Created tenant: {tenant.name} (id={tenant.id})")
    print(f"Created admin: {admin.email} / Admin@12345!")


async def _seed_properties(db: AsyncSession) -> None:
    from sqlalchemy import select
    from app.models.property import Property, PropertyPurpose, PropertySource, PropertyStatus, PropertyType
    from app.models.tenant import Tenant

    tenant = (await db.execute(select(Tenant).where(Tenant.slug == "sceptre-estate"))).scalar_one_or_none()
    if not tenant:
        print("No tenant found — skipping property seed.")
        return

    existing = (await db.execute(select(Property).where(Property.tenant_id == tenant.id))).scalars().first()
    if existing:
        print("Properties already seeded — skipping.")
        return

    sample_properties = [
        {
            "title": "Luxury 3BR Apartment in Dubai Marina",
            "description": "Stunning sea-view apartment with premium finishes and world-class amenities.",
            "property_type": PropertyType.apartment,
            "status": PropertyStatus.available,
            "purpose": PropertyPurpose.buy,
            "price_aed": 2_500_000,
            "bedrooms": 3,
            "bathrooms": 3,
            "area_sqft": 1850,
            "address": "Marina Gate 2, Dubai Marina, Dubai",
            "latitude": 25.0777,
            "longitude": 55.1390,
            "is_freehold": True,
            "is_golden_visa_eligible": True,
            "developer": "Select Group",
            "rera_number": "REA-2024-1001",
            "roi_estimated": 5.8,
            "images": [{"url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800", "caption": "Living area"}],
        },
        {
            "title": "Contemporary 1BR Studio in Business Bay",
            "description": "Modern studio with Burj Khalifa view, ideal for young professionals and investors.",
            "property_type": PropertyType.studio,
            "status": PropertyStatus.available,
            "purpose": PropertyPurpose.buy,
            "price_aed": 980_000,
            "bedrooms": 1,
            "bathrooms": 1,
            "area_sqft": 620,
            "address": "The Opus, Business Bay, Dubai",
            "latitude": 25.1869,
            "longitude": 55.2572,
            "is_freehold": True,
            "is_golden_visa_eligible": False,
            "developer": "Omniyat",
            "roi_estimated": 7.2,
            "images": [],
        },
        {
            "title": "4BR Villa on Palm Jumeirah",
            "description": "Exclusive beachfront villa with private pool and direct beach access.",
            "property_type": PropertyType.villa,
            "status": PropertyStatus.available,
            "purpose": PropertyPurpose.buy,
            "price_aed": 12_500_000,
            "bedrooms": 4,
            "bathrooms": 5,
            "area_sqft": 5200,
            "address": "Palm Fronds, Palm Jumeirah, Dubai",
            "latitude": 25.1124,
            "longitude": 55.1390,
            "is_freehold": True,
            "is_golden_visa_eligible": True,
            "developer": "Nakheel",
            "roi_estimated": 4.1,
            "images": [],
        },
        {
            "title": "2BR Apartment for Rent — JLT",
            "description": "Well-maintained apartment in Jumeirah Lake Towers with lake views.",
            "property_type": PropertyType.apartment,
            "status": PropertyStatus.available,
            "purpose": PropertyPurpose.rent,
            "price_aed": 95_000,
            "bedrooms": 2,
            "bathrooms": 2,
            "area_sqft": 1200,
            "address": "Cluster G, JLT, Dubai",
            "latitude": 25.0700,
            "longitude": 55.1430,
            "is_freehold": False,
            "is_golden_visa_eligible": False,
            "roi_estimated": None,
            "images": [],
        },
        {
            "title": "Off-Plan 2BR at Dubai Creek Harbour",
            "description": "Pre-launch pricing on premium Creek Tower views. Handover Q4 2027.",
            "property_type": PropertyType.apartment,
            "status": PropertyStatus.off_plan,
            "purpose": PropertyPurpose.buy,
            "price_aed": 1_850_000,
            "bedrooms": 2,
            "bathrooms": 2,
            "area_sqft": 1100,
            "address": "Creek Rise Tower 1, Dubai Creek Harbour",
            "latitude": 25.1975,
            "longitude": 55.3312,
            "is_off_plan": True,
            "is_freehold": True,
            "is_golden_visa_eligible": False,
            "developer": "Emaar",
            "payment_plan": {
                "on_booking": 10,
                "during_construction": 40,
                "on_handover": 50,
                "completion_date": "2027-12-01",
            },
            "roi_estimated": 6.5,
            "images": [],
        },
    ]

    import re

    for data in sample_properties:
        prop_id = uuid.uuid4()
        slug_base = re.sub(r"[^a-z0-9]+", "-", data["title"].lower()).strip("-")
        slug = f"{slug_base}-{str(prop_id)[:8]}"

        prop = Property(
            id=prop_id,
            tenant_id=tenant.id,
            slug=slug,
            source=PropertySource.csv,
            **{k: v for k, v in data.items()},
        )
        db.add(prop)

    await db.flush()
    print(f"Seeded {len(sample_properties)} properties.")


if __name__ == "__main__":
    asyncio.run(seed())
