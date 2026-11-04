import numpy as np
import pandas as pd
import pytest

from awg_analysis.data import normalize_program, parse_number, require_unique, wide_to_long
from awg_analysis.metrics import launch_metrics
from awg_analysis.models import fit_segment_model
from awg_analysis.pipeline import run


def test_none_category_is_distinct_from_unknown():
    result = normalize_program(pd.Series(["None", None, "", " AIM-A "]))
    assert result.tolist() == ["None", "Unknown", "Unknown", "AIM_A"]
    with pytest.raises(ValueError, match="Unrecognized"):
        normalize_program(pd.Series(["AIM typo"]))


def test_currency_keeps_returns_and_rejects_silent_zero():
    assert parse_number(pd.Series(["$1,234.50", "($10.50)", "0"])).tolist() == [1234.5, -10.5, 0]
    with pytest.raises(ValueError, match="malformed"):
        parse_number(pd.Series(["not supplied"]))


def test_join_dimensions_require_unique_keys():
    with pytest.raises(ValueError, match="duplicate"):
        require_unique(pd.DataFrame({"id": ["a", "a"]}), ["id"], "dimension")


def test_reshape_preserves_total_and_month_mapping():
    wide = pd.DataFrame({"store": ["S1", "S2"], "jan": [2, 3], "feb": [5, 7]})
    result = wide_to_long(wide, ["store"], {"jan": "2025-01", "feb": "2025-02"})
    assert len(result) == 4
    assert result.sales.sum() == 17
    assert result.month.nunique() == 2


def test_year_boundary_censoring_zero_roster_stores_and_net_returns():
    frames = {
        "stores": pd.DataFrame({"store_id": ["S1", "S2"], "program": ["None", "None"], "division": ["East", "East"]}),
        "items": pd.DataFrame({"item_id": ["I1", "I2", "I3"],
                               "launch_month": pd.PeriodIndex(["2024-11", "2025-02", "2024-10"], freq="M")}),
        "sales": pd.DataFrame({"store_id": ["S1"]*4, "item_id": ["I1"]*4,
                               "month": pd.PeriodIndex(["2024-11", "2024-12", "2025-01", "2025-02"],freq="M"),
                               "units": [99, 2, -1, 3], "sales": [990, 20, -10, 30]}),
        "observation_months": pd.DataFrame({"month": pd.period_range("2024-10", "2025-02", freq="M")})}
    result = launch_metrics(frames)
    total = result["program_3m"].iloc[0]
    assert total.n_stores == 2
    assert total.mean_sales_3m == 20  # (20 - 10 + 30) / 2, excluding launch month
    coverage = result["item_coverage_3m"].set_index("item_id")
    assert coverage.loc["I1", "coverage_pct"] == 50
    assert np.isnan(coverage.loc["I2", "coverage_pct"])
    assert coverage.loc["I3", "coverage_pct"] == 0  # observed, but no purchases


def test_missing_interior_followup_month_is_incomplete():
    frames = {
        "stores": pd.DataFrame({"store_id": ["S"], "program": ["None"], "division": ["East"]}),
        "items": pd.DataFrame({"item_id": ["I"], "launch_month": pd.PeriodIndex(["2024-11"], freq="M")}),
        "sales": pd.DataFrame({"store_id": ["S"], "item_id": ["I"],
                               "month": pd.PeriodIndex(["2024-12"], freq="M"), "units": [1], "sales": [10]}),
        "observation_months": pd.DataFrame({"month": pd.PeriodIndex(["2024-12", "2025-02"], freq="M")})}
    coverage = launch_metrics(frames)["item_coverage_3m"].iloc[0]
    assert not coverage.complete_3m
    assert coverage.observed_followup_months == 2
    assert np.isnan(coverage.coverage_pct)


def test_contrast_uses_baseline_within_segment_and_excludes_one_store_cell():
    rows = []
    for region, offset in [("East", 1), ("West", -0.5)]:
        for program, effect in [("None", 0), ("AIM_A", offset)]:
            for store in range(8):
                for item in range(5):
                    rows.append({"division": region, "program": program,
                                 "store_id": f"{region}-{program}-{store}",
                                 "sales_m12": np.expm1(3 + effect + store/20 + item/50)})
    rows += [{"division": "East", "program": "AIM_Both", "store_id": "ONLY_ONE", "sales_m12": 100}] * 40
    support, contrasts, diagnostics = fit_segment_model(pd.DataFrame(rows), "division")
    assert not support.loc[support.program.eq("AIM_Both"), "eligible"].any()
    values = contrasts.set_index("division").log1p_difference
    assert values["East"] == pytest.approx(1)
    assert values["West"] == pytest.approx(-0.5)
    assert diagnostics["n_store_clusters"] == 32
    assert (contrasts.ci_low <= contrasts.log1p_difference).all()
    assert (contrasts.ci_high >= contrasts.log1p_difference).all()


def test_private_inputs_use_a_separate_output_directory(tmp_path):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    with pytest.raises(ValueError, match="outside the public repository"):
        run(tmp_path, root/"reports/private", "private")
