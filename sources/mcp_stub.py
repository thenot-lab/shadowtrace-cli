"""Graceful stubs for sources that require live MCP sessions.

gmail / common_room / apollo / stripe_crm all need active MCP clients, which
this standalone Python process does not have. These stubs return empty with
a flagged reason so the audit log records the gap honestly.
"""
from __future__ import annotations
from typing import List
from .base import Record


REASON = "mcp_unavailable_in_standalone_python_runtime"


def gmail(_query: str) -> List[Record]:
    return []


def common_room(_query: str) -> List[Record]:
    return []


def apollo(_query: str) -> List[Record]:
    return []


def stripe_crm(_query: str) -> List[Record]:
    return []


def status() -> dict:
    return {s: REASON for s in ("gmail", "common_room", "apollo", "stripe_crm")}
