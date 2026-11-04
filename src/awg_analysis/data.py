"""Explicit input contracts and audited joins."""

from pathlib import Path
import numpy as np
import pandas as pd

PROGRAMS = ["None", "AIM_A", "AIM_B", "AIM_A & One Source",
            "AIM_B & One Source", "AIM_Both", "One Source"]
ALIASES = {"AIM-A": "AIM_A", "AIM-B": "AIM_B", "OneSource": "One Source"}
SCHEMAS = {
    "stores": ["store_id", "division", "program"],
    "items": ["item_id", "brand", "category", "launch_month"],
    "sales": ["store_id", "item_id", "month", "units", "sales"],
    "outcomes": ["store_id", "item_id", "sales_m12"],
    "observation_months": ["month"],
}


def normalize_program(values):
    """Preserve literal 'None'. Missing participation remains unknown."""
    cleaned = values.astype("string").str.strip().replace(ALIASES).fillna("Unknown")
    cleaned = cleaned.replace("", "Unknown")
    invalid = set(cleaned.unique()) - set(PROGRAMS + ["Unknown"])
    if invalid:
        raise ValueError(f"Unrecognized program categories: {sorted(invalid)}")
    return cleaned


def parse_number(values):
    """Parse currency and accounting negatives, rejecting malformed values."""
    text = values.astype("string").str.strip()
    text = text.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    text = text.str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    result = pd.to_numeric(text, errors="coerce")
    if result.isna().any() or not np.isfinite(result.astype(float)).all():
        raise ValueError("Numeric fields contain missing, malformed, or non-finite values")
    return result.astype(float)


def month_period(values, allow_missing=False):
    text = values.astype("string")
    valid = text.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])")
    if allow_missing:
        valid = valid | text.eq("")
        text = text.replace("", None)
    if not valid.all():
        raise ValueError("Months must use YYYY-MM")
    return pd.PeriodIndex(text, freq="M")


def require_unique(df, keys, label):
    if df[keys].isna().any().any() or df[keys].astype(str).eq("").any().any():
        raise ValueError(f"{label}: missing key")
    if df.duplicated(keys).any():
        raise ValueError(f"{label}: duplicate keys {keys}")


def load_data(directory):
    directory = Path(directory)
    frames = {}
    for name, columns in SCHEMAS.items():
        # Preserve the literal source category 'None' through explicit CSV parsing.
        frame = pd.read_csv(directory / f"{name}.csv", dtype=str, keep_default_na=False)
        if set(frame) != set(columns):
            raise ValueError(f"{name}: expected columns {columns}, received {list(frame)}")
        for column in columns:
            if frame[column].str.strip().eq("").any():
                if (name == "stores" and column == "program") or (name == "items" and column == "launch_month"):
                    continue
                raise ValueError(f"{name}: blank {column}")
        frames[name] = frame
    stores, items, sales, outcomes, months = (frames[k] for k in SCHEMAS)
    require_unique(stores, ["store_id"], "stores")
    require_unique(items, ["item_id"], "items (resolve repeated launches first)")
    require_unique(sales, ["store_id", "item_id", "month"], "monthly sales")
    require_unique(outcomes, ["store_id", "item_id"], "source m12 outcomes")
    require_unique(months, ["month"], "observation calendar")
    stores["program"] = normalize_program(stores.program)
    items["launch_month"] = month_period(items.launch_month, allow_missing=True)
    sales["month"] = month_period(sales.month)
    months["month"] = month_period(months.month)
    for column in ["units", "sales"]:
        sales[column] = parse_number(sales[column])
    outcomes["sales_m12"] = parse_number(outcomes.sales_m12)
    for name in ["sales", "outcomes"]:
        for key, dimension in [("store_id", stores), ("item_id", items)]:
            if not frames[name][key].isin(dimension[key]).all():
                raise ValueError(f"{name}: unmapped {key}; audit before joining")
    if not sales.month.isin(months.month).all():
        raise ValueError("Sales contain months outside the declared observation calendar")
    return frames


def join_outcomes(frames):
    return (frames["outcomes"]
            .merge(frames["stores"], on="store_id", how="left", validate="many_to_one")
            .merge(frames["items"][["item_id", "brand", "category"]],
                   on="item_id", how="left", validate="many_to_one"))


def wide_to_long(frame, id_columns, month_columns):
    """Reshape retail data using declared identifiers and an explicit month mapping."""
    if frame.duplicated(id_columns).any():
        raise ValueError("Wide data require unique identifier rows")
    if len(set(month_columns.values())) != len(month_columns):
        raise ValueError("Assign a distinct month to each wide column")
    long = frame.melt(id_vars=id_columns, value_vars=list(month_columns),
                      var_name="source_column", value_name="sales")
    long["month"] = month_period(long.source_column.map(month_columns))
    long["sales"] = parse_number(long.sales)
    return long.drop(columns="source_column")
