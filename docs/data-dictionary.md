# Canonical data dictionary

[Repository home](../README.md)

This five-table contract defines normalized project inputs stored in a separate local directory. The importer converts the original client workbooks into these tables. CSVs use UTF-8, and identifiers remain strings.

## stores.csv

| Column | Type | Meaning |
|---|---|---|
| store_id | unique string | Stable store identifier used for joins and store counts |
| division | string | Source division code |
| program | enum | Source participation category or `Unknown` |

Accepted labels: `None`, `AIM_A`, `AIM_B`, `AIM_A & One Source`, `AIM_B & One Source`, `AIM_Both`, `One Source`, `Unknown`. Aliases `AIM-A`, `AIM-B`, and `OneSource` are normalized. The loader validates categories against this list.

Participation is a static snapshot. A time-varying extension would add enrollment and exit dates.

## items.csv

| Column | Type | Meaning |
|---|---|---|
| item_id | unique string | Stable item identifier |
| brand | string | Product brand; `Unmapped` identifies metadata review items |
| category | string | Product category |
| launch_month | YYYY-MM or blank | Accepted launch month; blank identifies launch-date review items |

Product attributes use a unique item dimension. An accepted launch date enables early-window eligibility checks. Multiple business-confirmed launches can be represented in a future item-launch-event dimension.

## sales.csv

| Column | Type | Meaning |
|---|---|---|
| store_id | string | Foreign key to stores |
| item_id | string | Foreign key to items |
| month | YYYY-MM | Calendar month |
| units | numeric | Net billed quantity in source billing units |
| sales | numeric | Net AWG-to-store billed dollar amount |

Unique key: store_id + item_id + month. Underlying source records are summed to this grain. Returns retain their signed values. Numeric validation and accounting-currency parsing preserve the supplied measure.

## outcomes.csv

| Column | Type | Meaning |
|---|---|---|
| store_id | string | Foreign key to stores |
| item_id | string | Foreign key to items |
| sales_m12 | numeric | Source-indexed cumulative m12 sales |

Unique key: store_id + item_id. Model means describe the observed store-item outcome population. Early per-store KPI means use the declared roster population. These population definitions accompany their respective result tables.

## observation_months.csv

| Column | Type | Meaning |
|---|---|---|
| month | unique YYYY-MM | Declared complete source-feed month |

The local importer builds a provisional calendar from transaction months and records feed-completeness reconciliation in the import audit. All three required follow-up months must appear for a complete-window flag.

## Generated outputs

| Output | Grain and purpose |
|---|---|
| store_3m.csv | Roster store, with early net sales and billed quantity |
| program_3m.csv | Program-category store counts, totals, and per-store means |
| item_coverage_3m.csv | Item, launch date, follow-up status, active stores, denominator, coverage |
| window_sensitivity.csv | Complete-item counts and dollars for two window definitions |
| brand_support.csv / division_support.csv | Observed cell row counts, distinct stores, arithmetic/log means, eligibility |
| brand_contrasts.csv / division_contrasts.csv | Within-segment contrasts, pointwise intervals, raw and adjusted p-values |
| run_manifest.json | Input hashes, environment, row counts, cohort status, specifications, diagnostics |

Support tables list observed combinations and their model eligibility. Empty combinations retain an undefined status, preserving the distinction between observation support and zero-valued outcomes.
