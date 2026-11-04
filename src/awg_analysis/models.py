"""Observed-cell interaction models and within-segment contrasts."""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from .data import PROGRAMS


def fit_segment_model(outcomes, moderator, min_rows=30, min_stores=5):
    data = outcomes.loc[outcomes.program.isin(PROGRAMS)].copy()
    negative = int(data.sales_m12.lt(0).sum())
    # The log-outcome sample uses nonnegative cumulative sales; diagnostics track returns.
    data = data.loc[data.sales_m12.ge(0)].copy()
    data["log_sales"] = np.log1p(data.sales_m12)
    support = data.groupby([moderator, "program"], as_index=False).agg(
        n_rows=("store_id", "size"), n_stores=("store_id", "nunique"),
        mean_sales=("sales_m12", "mean"), mean_log_sales=("log_sales", "mean"))
    support["eligible"] = support.n_rows.ge(min_rows) & support.n_stores.ge(min_stores)
    eligible = support.loc[support.eligible, [moderator, "program"]]
    data = data.merge(eligible, on=[moderator, "program"], validate="many_to_one")
    if data.empty or data.store_id.nunique() < 2:
        raise ValueError(f"{moderator}: insufficient independent store support")
    data["cell"] = data.groupby([moderator, "program"], sort=True).ngroup().astype(str)
    # Estimate one parameter for each supported observed program-segment cell.
    model = smf.ols("log_sales ~ 0 + C(cell)", data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data.store_id}, use_t=True)
    means = data.groupby([moderator, "program"], as_index=False).first()
    names = list(model.params.index)
    cell_index = {(r[moderator], r["program"]): names.index(f"C(cell)[{r['cell']}]")
                  for _, r in means.iterrows()}
    # Joint contrasts test heterogeneity in supported program-group associations.
    interaction_constraints = []
    for program in PROGRAMS[1:]:
        segments = sorted(segment for segment, p in cell_index
                          if p == program and (segment, "None") in cell_index)
        if len(segments) < 2:
            continue
        reference = segments[0]
        for segment in segments[1:]:
            vector = np.zeros(len(names))
            for key, sign in [((segment, program), 1), ((segment, "None"), -1),
                              ((reference, program), -1), ((reference, "None"), 1)]:
                vector[cell_index[key]] += sign
            interaction_constraints.append(vector)
    joint = None
    if interaction_constraints:
        matrix = np.vstack(interaction_constraints)
        result = model.wald_test(matrix, use_f=True, scalar=True)
        joint = {"f_statistic": float(result.statistic), "p_value": float(result.pvalue),
                 "df_numerator": float(result.df_num), "df_denominator": float(result.df_denom),
                 "scope": "equality of supported program-vs-None contrasts across segments"}
    rows = []
    for segment, group in means.groupby(moderator, sort=True):
        baseline = group.loc[group.program.eq("None")]
        if baseline.empty:
            continue
        baseline_cell = baseline.iloc[0]["cell"]
        for _, row in group.loc[~group.program.eq("None")].iterrows():
            contrast = np.zeros(len(names))
            contrast[names.index(f"C(cell)[{row['cell']}]")] = 1
            contrast[names.index(f"C(cell)[{baseline_cell}]")] = -1
            result = model.t_test(contrast)
            low, high = result.conf_int()[0]
            effect = float(np.asarray(result.effect).item())
            rows.append({moderator: segment, "program": row.program,
                         "log1p_difference": effect, "ci_low": float(low), "ci_high": float(high),
                         "p_value": float(np.asarray(result.pvalue).item()),
                         "geometric_1plus_difference_pct": float(np.expm1(effect) * 100)})
    columns = [moderator, "program", "log1p_difference", "ci_low", "ci_high", "p_value",
               "geometric_1plus_difference_pct"]
    contrasts = pd.DataFrame(rows, columns=columns)
    if len(contrasts):
        contrasts["p_adjusted_bh"] = multipletests(contrasts.p_value, method="fdr_bh")[1]
        contrasts = contrasts.merge(support[[moderator, "program", "n_rows", "n_stores"]],
                                    on=[moderator, "program"], validate="one_to_one")
    diagnostics = {"moderator": moderator, "n_model_rows": int(model.nobs),
                   "n_store_clusters": int(data.store_id.nunique()),
                   "negative_outcome_rows_excluded": negative,
                   "unknown_program_rows_excluded": int((~outcomes.program.isin(PROGRAMS)).sum()),
                   "n_sparse_cells": int((~support.eligible).sum()),
                   "min_rows": min_rows, "min_stores": min_stores,
                   "r_squared": float(model.rsquared),
                   "interaction_joint_test": joint,
                   "formula": "log1p(sales_m12) ~ observed(program x segment) cells",
                   "covariance": "store-clustered, small-sample correction, t intervals",
                   "interpretation": "unadjusted within-segment program association"}
    return support, contrasts, diagnostics
