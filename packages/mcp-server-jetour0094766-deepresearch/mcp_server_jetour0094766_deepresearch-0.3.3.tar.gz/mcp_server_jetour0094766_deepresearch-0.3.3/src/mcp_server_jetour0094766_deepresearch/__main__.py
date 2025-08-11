#!/usr/bin/env python3
"""
DeepResearch MCP Server Entry Point
"""
import asyncio
import os
import sys
from .server import main

if __name__ == "__main__":
    asyncio.run(main())