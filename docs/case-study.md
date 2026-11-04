# Case study: retail programs and new-item performance

[Repository home](../README.md)

## Business context

AWG's AIM program automatically ships selected new items to participating stores, while One Source provides in-store merchandising support. The client project studied how participation relates to early purchasing and distribution, then examined the patterns across brands and divisions.

The business background describes monthly launches in 2024 and a quarterly launch plan in 2025. Introductory deals changed from a 90-day structure to a 60-day structure with a limited first-case credit. Auto-shipping eligibility also varies by brand. These details establish the context for comparing launch cohorts and interpreting product mix.

The analysis connects three decisions: how to measure early performance consistently, how to compare participation groups at the appropriate grain, and how to select useful brand/division combinations for further evaluation.

## Checkpoint 1: data foundation and metric design

The source monthly sales table contains **542,564 records**, establishing the preparation workload. The later regression sample is measured separately at store-item grain. Sales were cleaned, reshaped, and organized at **store × item × year × month** grain, then aligned with participation, product attributes, and launch information. The first client presentation explains the business question, comparison groups, metric definitions, and dataset structure on slides 3–7.

The initial comparison used four participation groups: AIM only, One Source only, both programs, and neither. Two KPI families connected the dataset to the business question:

- **Early performance:** billed quantity and net AWG billed sales in each item's three-month post-launch window, aggregated by store.
- **Item adoption:** the share of eligible stores with positive purchase activity for an item during that window.

The presentation added brand, category, and geographic views. It also identified participation timing, repeated launch records, and seasonal context as priorities for data review. The repository translates those priorities into explicit contracts and executable checks.

## Checkpoint 2: brand and division analysis

The second checkpoint used `log1p(cum_sales_m12)` as its outcome and seven program categories, with `None` as the reference. Separate `program × brand` and `program × division` OLS models provided a framework for comparing program associations within each segment.

The source results contain **93,108 store-item observations**, covering **five brands and nine divisions**. The brand model reports R² of **0.051**, and the division model reports R² of **0.014**, using conventional OLS standard errors.

Brand and regional plots and interaction-regression findings appear from slide 17 onward in the final client presentation. The complete presentation combines the project's overall-sales, category, brand, and regional workstreams. Client interviews and presentation discussions informed the interpretation and recommendations.

The [full second-checkpoint report](checkpoint-2.md) follows slides 17–31, covering the regression method, five-brand findings, sample matrix, all nine regional charts, and recommendations.

## Findings and business use

| Analytical finding | Evidence | Decision use |
|---|---|---|
| Total sales and per-store sales provide complementary views of participation groups | Final presentation, slides 4–5 | Compare scale alongside normalized performance |
| Program patterns vary across brands and divisions | Second-checkpoint notebook; final presentation, slides 17–30 | Build a segment-specific program evaluation plan |
| Independent store counts add context to cell-level estimates | Final presentation, slide 21; participation counts | Set evidence priorities for follow-up samples |
| The two interaction specifications summarize distinct dimensions of sales variation | Source R²: 0.051 and 0.014 | Extend the models with store, product, and timing information |
| Positive billed purchases provide an operational adoption measure | Program background and early-window KPIs | Track initial distribution and follow it with repeat-purchase measures |

The project delivers a structured basis for **brand- and division-specific pilot design**. Segment profiles, support tables, and clearly defined KPIs help focus the next round of evaluation on concrete program/product/location combinations.

## Reproducible portfolio implementation

The repository extends the original analysis with canonical schemas, validated joins, cross-year launch periods, distinct participation labels, complete-follow-up flags, and reusable Python functions. The original notebooks preserve the course transformation reference and both checkpoint analyses. The modular code provides a supplementary local workflow.

The current model estimates supported observed-cell means and calculates within-segment program-vs-`None` contrasts. Store-clustered intervals account for repeated observations from the same store. Local client-data execution supports the supplementary implementation, and original report charts document the client-facing outputs. [Design decisions](decision-log.md)

## Analytical scope

**Outcome.** Monthly values measure AWG-to-store net billed sales and quantity. The cumulative model target is the supplied `m12` field, indexed according to the source table. The local arithmetic check reconciles that cumulative value to its twelve supplied monthly components.

**Population.** Early KPIs use a declared store roster and accepted launch dates. A common-eligibility and complete-feed assumption defines zero-purchase treatment. The import audit records calendar interpretation, product mappings, and review items.

**Comparisons.** Models estimate unadjusted associations within brands or divisions using a static participation snapshot. Support screening uses both observations and distinct stores. Store clustering, pointwise intervals, and BH-adjusted p-values provide complementary information for interpreting the comparisons.

## Next analytical stage

1. Add enrollment and exit dates, store characteristics, product controls, and pre-period outcomes to align program exposure and comparison groups.
2. Reconcile source month indexing with launch dates and define matched follow-up windows across cohorts.
3. Refine item-store eligibility using assortment, division availability, openings, and closures; validate feed completeness by period.
4. Track first shipments, repeat purchases, shelf execution, and contribution margin after program costs.
5. Predefine pilot candidates and outcomes, then evaluate incremental performance through a controlled or randomized rollout where feasible.

These steps extend the project's KPI and segmentation framework into a more detailed program evaluation plan.
