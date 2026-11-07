# AWG Retail Program Participation Analysis

English | [简体中文](README.zh-CN.md)

A retail program analysis for AWG, completed as a **UIUC BADM550 client project**.

**Python · pandas · NumPy · statsmodels · Matplotlib · seaborn · Excel**

## Project at a glance

- **Task:** Compare new-item purchasing and store coverage across AIM auto-ship and One Source merchandising participation groups to guide program evaluation.
- **Data preparation:** Cleaned and integrated **542,564 monthly records** through reshaping, identifier standardization, and multi-table joins at store × item × month grain.
- **KPI design:** Defined cumulative sales, billed quantity, and purchase-based store coverage over the three full months following each item's launch, with explicit windows and denominators.
- **Regression:** Analyzed **93,108 store-item observations** across **5 brands and 9 divisions**, using separate program × brand and program × division OLS interaction models.

## My contributions

- **Data preparation:** Reshaped, cleaned, fuzzy-matched, and integrated **540K+ raw records**, establishing **store × item × month** as the base analytical grain.
- **KPI development · Checkpoint 1:** Framed new-item performance comparisons across program groups; used Python to calculate **three-month cumulative sales and billed quantity by store × launch cohort**, plus **item-level store coverage**.
- **Regression analysis · Checkpoint 2:** Built **program × brand OLS interaction models** in Python and visualized cumulative sales patterns across **5 brands** and participation groups.
- **Client presentations:** Created and presented slides covering KPI design, regression methods, and brand findings across both checkpoints.

## Key findings

- Stores enrolled in both programs had the **highest mean early sales per store** in the first-checkpoint comparison.
- Brand and division profiles identified distinct program patterns, informing **brand-specific recommendations and regional pilot priorities** presented across two client briefings.

![Mean log cumulative sales by brand and program participation](reports/presentation-excerpts/historical_brand_program_log_sales.png)

## Explore the project

| Content | Files |
|---|---|
| Data preparation and KPIs | [Checkpoint 1 notebook](notebooks/01_checkpoint1_data_and_metrics.ipynb) · [Metric definitions](docs/methodology.md) |
| Brand and division analysis | [Checkpoint 2 notebook](notebooks/02_checkpoint2_brand_and_division.ipynb) · [Complete findings](docs/checkpoint-2.md) |
| Client deliverables | [Two complete presentations](presentations/README.md) · [Original chart gallery](reports/presentation-excerpts/README.md) |

Client workbooks are stored locally. Follow the [execution guide](docs/reproducibility.md) for setup and required inputs.

[Case study](docs/case-study.md) · [Project deliverables](docs/project-deliverables.md) · [Original code archive](notebooks/archive/README.md) · [License](LICENSE) · [Attribution](NOTICE.md)
