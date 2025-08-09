#!/usr/bin/env python3
"""Quick live API test for ukcompanies package."""

import asyncio
import os
from ukcompanies import AsyncClient

async def test_live_api():
    """Test with real Companies House API."""
    api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
    
    if not api_key:
        print("❌ Set COMPANIES_HOUSE_API_KEY environment variable")
        return False
    
    try:
        async with AsyncClient(api_key=api_key) as client:
            # Test with Tesco PLC (known company)
            company = await client.profile("00445790")
            print(f"✅ Live API test successful!")
            print(f"Company: {company.company_name}")
            print(f"Status: {company.company_status}")
            return True
    except Exception as e:
        print(f"❌ Live API test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_live_api())
    exit(0 if success else 1)