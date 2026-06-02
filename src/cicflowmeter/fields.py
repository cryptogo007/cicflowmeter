"""Exportable flow feature column names and field-selection helpers."""

from __future__ import annotations

# Canonical CSV column order (matches Flow.get_data).
EXPORT_FIELD_NAMES: tuple[str, ...] = (
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "protocol",
    "timestamp",
    "flow_duration",
    "flow_byts_s",
    "flow_pkts_s",
    "fwd_pkts_s",
    "bwd_pkts_s",
    "tot_fwd_pkts",
    "tot_bwd_pkts",
    "totlen_fwd_pkts",
    "totlen_bwd_pkts",
    "fwd_pkt_len_max",
    "fwd_pkt_len_min",
    "fwd_pkt_len_mean",
    "fwd_pkt_len_std",
    "bwd_pkt_len_max",
    "bwd_pkt_len_min",
    "bwd_pkt_len_mean",
    "bwd_pkt_len_std",
    "pkt_len_max",
    "pkt_len_min",
    "pkt_len_mean",
    "pkt_len_std",
    "pkt_len_var",
    "fwd_header_len",
    "bwd_header_len",
    "fwd_seg_size_min",
    "fwd_act_data_pkts",
    "flow_iat_mean",
    "flow_iat_max",
    "flow_iat_min",
    "flow_iat_std",
    "fwd_iat_tot",
    "fwd_iat_max",
    "fwd_iat_min",
    "fwd_iat_mean",
    "fwd_iat_std",
    "bwd_iat_tot",
    "bwd_iat_max",
    "bwd_iat_min",
    "bwd_iat_mean",
    "bwd_iat_std",
    "fwd_psh_flags",
    "bwd_psh_flags",
    "fwd_urg_flags",
    "bwd_urg_flags",
    "fin_flag_cnt",
    "syn_flag_cnt",
    "rst_flag_cnt",
    "psh_flag_cnt",
    "ack_flag_cnt",
    "urg_flag_cnt",
    "ece_flag_cnt",
    "down_up_ratio",
    "pkt_size_avg",
    "init_fwd_win_byts",
    "init_bwd_win_byts",
    "active_max",
    "active_min",
    "active_mean",
    "active_std",
    "idle_max",
    "idle_min",
    "idle_mean",
    "idle_std",
    "fwd_byts_b_avg",
    "fwd_pkts_b_avg",
    "bwd_byts_b_avg",
    "bwd_pkts_b_avg",
    "fwd_blk_rate_avg",
    "bwd_blk_rate_avg",
    "fwd_seg_size_avg",
    "bwd_seg_size_avg",
    "cwr_flag_count",
    "subflow_fwd_pkts",
    "subflow_bwd_pkts",
    "subflow_fwd_byts",
    "subflow_bwd_byts",
)

EXPORT_FIELD_SET = frozenset(EXPORT_FIELD_NAMES)

# Grouped labels for the GUI field picker.
FIELD_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Endpoints",
        (
            "src_ip",
            "dst_ip",
            "src_port",
            "dst_port",
            "protocol",
            "timestamp",
        ),
    ),
    (
        "Flow rates & duration",
        (
            "flow_duration",
            "flow_byts_s",
            "flow_pkts_s",
            "fwd_pkts_s",
            "bwd_pkts_s",
        ),
    ),
    (
        "Packet counts",
        ("tot_fwd_pkts", "tot_bwd_pkts", "fwd_act_data_pkts"),
    ),
    (
        "Forward packet length",
        (
            "totlen_fwd_pkts",
            "fwd_pkt_len_max",
            "fwd_pkt_len_min",
            "fwd_pkt_len_mean",
            "fwd_pkt_len_std",
            "fwd_seg_size_avg",
            "fwd_seg_size_min",
        ),
    ),
    (
        "Backward packet length",
        (
            "totlen_bwd_pkts",
            "bwd_pkt_len_max",
            "bwd_pkt_len_min",
            "bwd_pkt_len_mean",
            "bwd_pkt_len_std",
            "bwd_seg_size_avg",
        ),
    ),
    (
        "Combined packet length",
        (
            "pkt_len_max",
            "pkt_len_min",
            "pkt_len_mean",
            "pkt_len_std",
            "pkt_len_var",
            "pkt_size_avg",
        ),
    ),
    (
        "Headers",
        ("fwd_header_len", "bwd_header_len"),
    ),
    (
        "Inter-arrival time",
        (
            "flow_iat_mean",
            "flow_iat_max",
            "flow_iat_min",
            "flow_iat_std",
            "fwd_iat_tot",
            "fwd_iat_max",
            "fwd_iat_min",
            "fwd_iat_mean",
            "fwd_iat_std",
            "bwd_iat_tot",
            "bwd_iat_max",
            "bwd_iat_min",
            "bwd_iat_mean",
            "bwd_iat_std",
        ),
    ),
    (
        "TCP flags",
        (
            "fwd_psh_flags",
            "bwd_psh_flags",
            "fwd_urg_flags",
            "bwd_urg_flags",
            "fin_flag_cnt",
            "syn_flag_cnt",
            "rst_flag_cnt",
            "psh_flag_cnt",
            "ack_flag_cnt",
            "urg_flag_cnt",
            "ece_flag_cnt",
            "cwr_flag_count",
        ),
    ),
    (
        "Windows & ratio",
        ("down_up_ratio", "init_fwd_win_byts", "init_bwd_win_byts"),
    ),
    (
        "Active / idle",
        (
            "active_max",
            "active_min",
            "active_mean",
            "active_std",
            "idle_max",
            "idle_min",
            "idle_mean",
            "idle_std",
        ),
    ),
    (
        "Bulk & subflow",
        (
            "fwd_byts_b_avg",
            "fwd_pkts_b_avg",
            "bwd_byts_b_avg",
            "bwd_pkts_b_avg",
            "fwd_blk_rate_avg",
            "bwd_blk_rate_avg",
            "subflow_fwd_pkts",
            "subflow_bwd_pkts",
            "subflow_fwd_byts",
            "subflow_bwd_byts",
        ),
    ),
)


def parse_export_fields(fields: str | list[str] | None) -> list[str] | None:
    """Parse and validate a field selection.

    Returns None when all columns should be exported.
    Raises ValueError for unknown names or an empty selection.
    """
    if fields is None:
        return None
    if isinstance(fields, str):
        raw = [f.strip() for f in fields.split(",") if f.strip()]
    else:
        raw = [str(f).strip() for f in fields if str(f).strip()]

    if not raw:
        return None

    unknown = sorted({name for name in raw if name not in EXPORT_FIELD_SET})
    if unknown:
        raise ValueError(
            "Unknown export field(s): "
            + ", ".join(unknown)
            + ". Use --list-fields to see valid names."
        )

    # Preserve user order while dropping duplicates.
    seen: set[str] = set()
    ordered: list[str] = []
    for name in raw:
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def filter_export_data(data: dict, include_fields: list[str] | None) -> dict:
    """Return only selected keys, in canonical column order."""
    if include_fields is None:
        return data
    return {name: data[name] for name in include_fields if name in data}


def fields_to_csv_arg(fields: list[str] | None) -> str | None:
    """Serialize a field list for CLI/GUI job requests."""
    if not fields:
        return None
    return ",".join(fields)


def selection_summary(fields: list[str] | None) -> str:
    total = len(EXPORT_FIELD_NAMES)
    if fields is None:
        return f"All {total} columns"
    count = len(fields)
    if count == total:
        return f"All {total} columns"
    return f"{count} of {total} columns selected"
