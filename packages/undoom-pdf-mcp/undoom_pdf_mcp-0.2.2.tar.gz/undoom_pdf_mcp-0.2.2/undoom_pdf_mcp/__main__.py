#!/usr/bin/env python3
"""
__main__.py - 支持 python -m undoom_pdf_mcp 运行
"""

import asyncio
from .main import main as async_main

def main():
    """同步入口点函数"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()