"""Launch-relative metrics with explicit denominators and censoring."""

import pandas as pd


def launch_metrics(frames):
    stores, items, sales = (frames[k] for k in ["stores", "items", "sales"])
    available = set(frames["observation_months"].month)
    status = items[["item_id", "launch_month"]].copy()
    status["observed_followup_months"] = status.launch_month.map(
        lambda launch: sum(launch + offset in available for offset in (1, 2, 3)))
    status["complete_3m"] = status.observed_followup_months.eq(3)
    # An alternate launch-inclusive window provides a sensitivity comparison.
    status["complete_including_launch"] = status.launch_month.map(
        lambda launch: all(launch + offset in available for offset in (0, 1, 2)))
    joined = sales.merge(status, on="item_id", validate="many_to_one")
    joined["offset"] = (joined.month.astype("int64") - joined.launch_month.astype("int64"))
    window = joined.loc[joined.complete_3m & joined.offset.between(1, 3)].copy()
    totals = window.groupby("store_id", as_index=False).agg(
        sales_3m=("sales", "sum"), units_3m=("units", "sum"))
    # The mean's denominator includes all roster stores, including zero-purchase stores.
    store_totals = stores.merge(totals, on="store_id", how="left", validate="one_to_one")
    store_totals[["sales_3m", "units_3m"]] = store_totals[["sales_3m", "units_3m"]].fillna(0)
    summary = store_totals.groupby("program", as_index=False).agg(
        n_stores=("store_id", "nunique"), total_sales_3m=("sales_3m", "sum"),
        mean_sales_3m=("sales_3m", "mean"), mean_units_3m=("units_3m", "mean"))
    coverage = status.merge(
        window.loc[window.units.gt(0)].groupby("item_id").store_id.nunique()
        .rename("active_stores"), on="item_id", how="left", validate="one_to_one")
    coverage["eligible_stores"] = len(stores)
    # Coverage status distinguishes follow-up review items from observed zero activity.
    complete = coverage.complete_3m
    coverage.loc[complete, "active_stores"] = coverage.loc[complete, "active_stores"].fillna(0)
    coverage.loc[~complete, "active_stores"] = float("nan")
    coverage["coverage_pct"] = 100 * coverage.active_stores / coverage.eligible_stores
    alternate = joined.loc[joined.complete_including_launch & joined.offset.between(0, 2)]
    sensitivity = pd.DataFrame([
        {"window": "L+1 to L+3 (primary)", "n_complete_items": int(status.complete_3m.sum()),
         "net_sales": float(window.sales.sum())},
        {"window": "L to L+2 (sensitivity)",
         "n_complete_items": int(status.complete_including_launch.sum()),
         "net_sales": float(alternate.sales.sum())},
    ])
    return {"store_3m": store_totals, "program_3m": summary,
            "item_coverage_3m": coverage, "window_sensitivity": sensitivity}
