"""Pytest-discoverable wrapper for the Sophie verification fixture.

The fixture in test_v7_1_sophie.py exposes a `run()` function that returns
an assertion report. This wrapper makes CI pick it up by exposing each
assertion as its own pytest test, so failures surface individually.
"""

from __future__ import annotations

import pytest
from shadowtrace.tests.test_v7_1_sophie import run as _run


@pytest.fixture(scope="module")
def sophie_report():
    return _run()


def test_overall_pass_rate(sophie_report):
    summary = sophie_report.get("summary", {})
    assert summary.get("passed") == summary.get("total"), (
        f"{summary.get('passed')}/{summary.get('total')} passed; "
        f"failures: {[a['name'] for a in sophie_report['assertions'] if not a['pass']]}"
    )


def test_each_assertion(sophie_report):
    failures = [a for a in sophie_report["assertions"] if not a["pass"]]
    assert not failures, "\n".join(
        f"{a['name']}: {a.get('detail', '(no detail)')}" for a in failures
    )
