#!/usr/bin/env python3
"""
__main__.py - 支持 python -m undoom_pdf_mcp 运行
"""

from .main import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())