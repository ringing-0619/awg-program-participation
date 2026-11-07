# Project work and deliverables

[Repository home](../README.md)

The project connects retail data preparation, KPI design, regression analysis, and client recommendations through two analytical checkpoints.

| Workstream | Completed work and result | Deliverable |
|---|---|---|
| Data preparation | Cleaned and reshaped 542,564 monthly source records; standardized identifiers and integrated store, product, launch, and participation tables | [Checkpoint 1 notebook](../notebooks/01_checkpoint1_data_and_metrics.ipynb) |
| Metric design | Defined store-item-month grain, launch-window sales and billed quantity, and purchase-based store coverage with explicit windows and denominators | [Methodology](methodology.md), [data dictionary](data-dictionary.md) |
| Early performance | Compared participation groups using total and per-store early sales; the combined-program group had the highest mean early sales in the first-checkpoint comparison | [Early-sales chart](../reports/presentation-excerpts/historical_early_sales_by_program.png), [16-slide presentation](../presentations/checkpoint-1-client-presentation.pptx) |
| Brand and regional analysis | Analyzed 93,108 store-item observations across 5 brands and 9 divisions using separate program-by-brand and program-by-division OLS interaction models | [Checkpoint 2 notebook](../notebooks/02_checkpoint2_brand_and_division.ipynb), [complete findings](checkpoint-2.md) |
| Client communication | Connected client interviews, metric definitions, segment profiles, and recommendations across two client presentations | [Complete presentations](../presentations/README.md) |
| Reproducible analysis | Preserved original source code, documented execution changes, and packaged reusable metric and model functions with validation checks | [Original notebook archive](../notebooks/archive/README.md), [execution guide](reproducibility.md), [Python modules](../src/awg_analysis) |

The resulting KPI framework and brand/division profiles support targeted program evaluation and pilot design. Twelve original chart assets, a KPI slide preview, and both complete presentations provide the client-facing evidence alongside the analytical code.
