"""
BaaS SMS/MMS MCP Server

A Model Context Protocol server for SMS and MMS messaging services.
"""

__version__ = "0.1.4"
__author__ = "mBaaS Team"
__email__ = "jjunmo@mbaas.kr"

from .server import main

__all__ = ["main"]