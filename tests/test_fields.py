import pytest

from cicflowmeter.fields import (
    EXPORT_FIELD_NAMES,
    filter_export_data,
    parse_export_fields,
    selection_summary,
)


def test_export_field_count():
    assert len(EXPORT_FIELD_NAMES) == 82


def test_parse_export_fields_none_and_empty():
    assert parse_export_fields(None) is None
    assert parse_export_fields("") is None
    assert parse_export_fields("  ,  ") is None


def test_parse_export_fields_subset():
    parsed = parse_export_fields("src_ip,fwd_pkt_len_mean,src_ip")
    assert parsed == ["src_ip", "fwd_pkt_len_mean"]


def test_parse_export_fields_unknown():
    with pytest.raises(ValueError, match="Unknown export field"):
        parse_export_fields("src_ip,not_a_real_column")


def test_filter_export_data_order():
    data = {"a": 1, "b": 2, "c": 3}
    filtered = filter_export_data(data, ["c", "a"])
    assert list(filtered.keys()) == ["c", "a"]
    assert filtered == {"c": 3, "a": 1}


def test_selection_summary():
    assert selection_summary(None) == "All 82 columns"
    assert selection_summary(["src_ip", "dst_ip"]) == "2 of 82 columns selected"
