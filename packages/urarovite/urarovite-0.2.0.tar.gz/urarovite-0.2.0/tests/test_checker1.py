import pandas as pd
from urarovite.checker import checker1


def test_checker1_all_valid():
    row = pd.Series(
        {
            "verification_field_ranges": "'Tab One'!A1:B2@@'Another'!C3@@'T'!Z1"  # all quoted
        }
    )
    res = checker1.run(row)
    assert res["checker"] == "sheet_name_leading_quoted"
    assert res["total_segments"] == 3
    assert res["ok"] is True
    assert res["failing_segments"] == []


def test_checker1_invalid_unquoted():
    row = pd.Series(
        {
            "verification_field_ranges": "Tab One!A1:B2"  # missing quotes
        }
    )
    res = checker1.run(row)
    assert res["ok"] is False
    assert res["total_segments"] == 1
    assert res["failing_segments"] == ["Tab One!A1:B2"]


def test_checker1_mixed():
    row = pd.Series(
        {"verification_field_ranges": "'Good'!A1@@Bad!B2:B5@@'Also Good'!C1"}
    )
    res = checker1.run(row)
    assert res["ok"] is False
    assert res["total_segments"] == 3
    assert res["failing_segments"] == ["Bad!B2:B5"]
