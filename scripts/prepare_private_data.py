"""Import the local project workbooks into canonical CSVs outside the public repository.

The portfolio workflow applies explicit data contracts and preserves source m12 outcomes.
The import audit records source mappings, working assumptions, and business-review tasks.
"""

import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd


def identifier(values):
    return pd.to_numeric(values, errors="raise").astype("int64").astype(str)


def prepare(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    project = Path(__file__).resolve().parents[1]
    if destination == project or project in destination.parents:
        raise ValueError("Private normalized files must stay outside the public repository")
    destination.mkdir(parents=True, exist_ok=True)
    names = ["dv_dataset_with_all_program_info.xlsx", "AWG All Store List 10.1.xlsx",
             "all_month.xlsx", "Sales_Data_Raw.xlsx"]
    audit = {"method": "portfolio implementation with explicit contracts and source-outcome preservation",
             "input_sha256": {name: hashlib.sha256((source/name).read_bytes()).hexdigest() for name in names}}
    final = pd.read_excel(source/names[0], sheet_name="dv_dataset_with_all_program_inf",
                         keep_default_na=False,
                         usecols=["store_code", "item_code", "division_code", "program_aim_a_b",
                                  "brand", "categories", "cum_sales_m12"])
    final = final.rename(columns={"store_code": "store_id", "item_code": "item_id",
                                  "division_code": "division", "program_aim_a_b": "program",
                                  "categories": "category", "cum_sales_m12": "sales_m12"})
    for key in ["store_id", "item_id"]:
        final[key] = identifier(final[key])
    if final.duplicated(["store_id", "item_id"]).any():
        raise ValueError("Final source outcomes are not unique at store-item grain")
    store_snapshot = final[["store_id", "division", "program"]].drop_duplicates()
    item_snapshot = final[["item_id", "brand", "category"]].drop_duplicates()
    if store_snapshot.duplicated("store_id").any() or item_snapshot.duplicated("item_id").any():
        raise ValueError("Final source dimension attributes conflict")
    master = pd.read_excel(source/names[1], usecols=["Store #", "Division Code"])
    master.columns = ["store_id", "master_division"]
    master["store_id"] = identifier(master.store_id)
    master["master_division"] = master.master_division.str.strip().str.lower()
    audit["master_duplicate_rows_removed"] = int(master.duplicated().sum())
    master = master.drop_duplicates()
    if master.duplicated("store_id").any():
        raise ValueError("Master store divisions conflict")
    if not final.store_id.isin(master.store_id).all():
        raise ValueError("Final outcomes contain stores absent from the master roster")
    stores = master.merge(store_snapshot, on="store_id", how="left", validate="one_to_one")
    mismatch = stores.division.notna() & stores.division.ne(stores.master_division)
    if mismatch.any():
        raise ValueError("Master and final snapshot divisions disagree")
    stores["division"] = stores.master_division
    stores["program"] = stores.program.fillna("Unknown").replace("", "Unknown")
    audit["master_stores"] = len(stores)
    audit["unknown_program_stores"] = int(stores.program.eq("Unknown").sum())
    launches = pd.read_excel(source/names[2], usecols=["Item_Code", "year", "month"])
    launches = launches.rename(columns={"Item_Code": "item_id"})
    launches["item_id"] = identifier(launches.item_id)
    invalid = ~launches.year.isin([2024, 2025]) | ~launches.month.between(1, 12)
    quarantine = launches.loc[invalid].assign(reason="outside documented 2024-2025 launch range")
    launches = launches.loc[~invalid].drop_duplicates()
    repeated = launches.groupby("item_id").size().loc[lambda x: x.gt(1)].index
    quarantine = pd.concat([quarantine, launches.loc[launches.item_id.isin(repeated)].assign(
        reason="multiple launch dates; requires business adjudication")], ignore_index=True)
    launches = launches.loc[~launches.item_id.isin(repeated)].copy()
    launches["launch_month"] = launches.year.astype(int).astype(str) + "-" + launches.month.astype(int).astype(str).str.zfill(2)
    items = item_snapshot.merge(launches[["item_id", "launch_month"]], on="item_id",
                                how="outer", validate="one_to_one")
    items[["brand", "category"]] = items[["brand", "category"]].fillna("Unmapped")
    items["launch_month"] = items.launch_month.fillna("")
    audit["launch_rows_quarantined"] = len(quarantine)
    audit["multiple_valid_launch_items_quarantined"] = len(repeated)
    audit["items_without_accepted_launch"] = int(items.launch_month.eq("").sum())
    print("Reading monthly sales workbook...", flush=True)
    raw = pd.read_excel(source/names[3], usecols=["Fiscal Year", "Calendar Month Nbr", "Store_Code",
                                                "Item_Code", "Billed Quantity", "Extended AWG Sell"])
    raw.columns = ["year", "calendar_month", "store_id", "item_id", "units", "sales"]
    for key in ["store_id", "item_id"]:
        raw[key] = identifier(raw[key])
    if not raw.calendar_month.between(1, 12).all():
        raise ValueError("Invalid calendar months")
    raw["month"] = raw.year.astype(int).astype(str) + "-" + raw.calendar_month.astype(int).astype(str).str.zfill(2)
    observed = raw[["month"]].drop_duplicates().sort_values("month")
    matched = raw.store_id.isin(stores.store_id) & raw.item_id.isin(items.item_id)
    audit["raw_sales_rows"] = len(raw)
    audit["sales_rows_outside_canonical_universe"] = int((~matched).sum())
    selected = raw.loc[matched]
    for column in ["units", "sales"]:
        selected = selected.copy() if column == "units" else selected
        selected[column] = pd.to_numeric(selected[column], errors="raise")
        if selected[column].isna().any():
            raise ValueError("Missing numeric sales value requires source review")
    sales = selected.groupby(["store_id", "item_id", "month"], as_index=False)[["units", "sales"]].sum()
    audit["monthly_sales_rows"] = len(sales)
    audit["source_outcome_rows"] = len(final)
    audit["assumptions"] = [
        "Working calendar uses Fiscal Year with Calendar Month Nbr; business-calendar reconciliation is a validation step.",
        "Observed source months define a provisional complete-feed calendar; validate completeness against source delivery records.",
        "Zero-purchase treatment uses complete-feed and common roster-eligibility assumptions; refine eligibility with item-store assortment data.",
        "Participation uses the final static snapshot; enrollment and exit dates are next-stage exposure inputs.",
        "Product attributes use the final workbook mapping; preserve upstream mapping reconciliation as a business-review task.",
        "The model preserves source-indexed cumulative m12 sales; reconcile month indexing for launch-aligned follow-up analysis.",
        "Launch-date review records retain original values for business confirmation."]
    stores[["store_id", "division", "program"]].to_csv(destination/"stores.csv", index=False)
    items.to_csv(destination/"items.csv", index=False)
    sales.to_csv(destination/"sales.csv", index=False)
    final[["store_id", "item_id", "sales_m12"]].to_csv(destination/"outcomes.csv", index=False)
    observed.to_csv(destination/"observation_months.csv", index=False)
    quarantine.to_csv(destination/"launch_quarantine.csv", index=False)
    (destination/"import_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({k: v for k, v in audit.items() if k not in ["input_sha256", "assumptions"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.output)
