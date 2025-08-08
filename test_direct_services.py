#!/usr/bin/env python3
"""Test script to verify direct service imports work correctly."""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_imports():
    """Test that we can import and use the direct services function."""
    try:
        from basic_memory.mcp.tools.utils import get_direct_services
        print("✓ Successfully imported get_direct_services")
        
        try:
            services = await get_direct_services()
            print("✓ Successfully called get_direct_services")
            print(f"✓ Got services: {list(services.keys())}")
        except Exception as e:
            print(f"⚠ get_direct_services call failed (expected if no project setup): {e}")
            
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_imports())
    sys.exit(0 if success else 1)
