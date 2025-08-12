"""Checker 1: Sheet name quoting in verification_field_ranges

Spec:
Given a row whose `verification_field_ranges` column contains multiple A1
ranges separated by `@@`, verify that each range segment starts with a sheet
name wrapped in single quotes when the tab name contains spaces (or any
non-alphanumeric underscore characters). Simpler rule here: every segment
must begin with a quoted sheet name pattern `'Name'!`.

Examples:
  Valid:   'March 2025'!A2:A91
  Invalid: March 2025'!A2:A91  (missing leading quote)

Return value (dict):
  {
    'checker': 'sheet_name_leading_quoted',
    'ok': bool,                # True if all segments quoted
    'total_segments': int,
    'failing_segments': [...], # segments missing proper leading quote
    'original': str            # original ranges string
  }

The public API: run(row_or_str, field='verification_field_ranges')
  - Accepts either a pandas Series (row) or a raw string for convenience.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any

import pandas as pd


CHECKER_NAME = "sheet_name_leading_quoted"

# Opening quote, one or more non-quote chars, closing quote, exclamation point.
# A segment is considered correctly quoted if it matches one of:
#   '^'[^']+'!'   (sheet + any following range/address)
#   '^'[^']+'$'   (entire sheet reference selecting whole sheet)
# (Anything after the ! is ignored for this simple checker.)
SHEET_PREFIX_RE = re.compile(r"^'[^']+'(!|$)")


def _split_segments(ranges_str: str) -> List[str]:
    return [seg.strip() for seg in ranges_str.split("@@") if seg.strip()]


def segment_is_quoted(segment: str) -> bool:
    return bool(SHEET_PREFIX_RE.match(segment))


def run(row_or_str: str | pd.Series, field: str = "verification_field_ranges") -> Dict[str, Any]:
    if isinstance(row_or_str, str):
        ranges_str = row_or_str
    else:
        ranges_str = row_or_str.get(field, "")
    segments = _split_segments(ranges_str)
    failing = [s for s in segments if not segment_is_quoted(s)]
    return {
        "checker": CHECKER_NAME,
        "ok": len(failing) == 0,
        "total_segments": len(segments),
        "failing_segments": failing,
        "original": ranges_str,
    }


# Backwards compatible helper name
run_detailed = run


if __name__ == "__main__":  # Simple CLI
    # Hard coded test cases
    test_cases = [
        # Valid cases
        ("'March 2025'!A2:A91@@'Sheet1'!B1", True),
        ("'Tab'!A1", True),
        ("'A'!A1@@'B'!B2:B5", True),
        # Invalid cases
        ("March 2025'!A2:A91@@'Sheet1'!B1", False),
        ("'Tab'!A1@@Sheet2!B2", False),
        ("Sheet!A1", False),
        ("'A'!A1@@B!B2:B5", False),
    ]

    for ranges_str, expected_ok in test_cases:
        mock_row = pd.Series({"verification_field_ranges": ranges_str})
        result = run(ranges_str)
        print(f"Input: {ranges_str}\nResult: {result}\n")
        assert result["ok"] == expected_ok, f"Test failed for: {ranges_str}"
    print("All tests passed.")
