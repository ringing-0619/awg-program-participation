# Methodology and metric definitions

[Repository home](../README.md)

## Analytical grain and data quality

| Table | Grain | Join rule |
|---|---|---|
| Store roster | One row per store | Unique store identifier |
| Product/launch dimension | One row per item, with launch-date review status | Unique item identifier |
| Monthly sales | Store × item × calendar month | Aggregate valid source records to this grain |
| Source cumulative outcome | Store × item | Join store/product attributes many-to-one |
| Store performance | Store | Sum each item's complete early window once |
| Adoption coverage | Item | Distinct active stores / declared eligible roster |

Identifiers remain strings. Validation checks key uniqueness, foreign keys, numeric values, month formats, and program categories. Numeric fields use explicit parsing; participation and launch-date review statuses have their own representations.

## Launch window and follow-up status

For item $i$ with launch month $L_i$, the primary window is:

$$W_i = \{L_i+1, L_i+2, L_i+3\}.$$

The window comprises the three full months following launch. Calendar-period arithmetic supports year boundaries: a November launch uses December, January, and February.

Complete-window metrics use items with all three follow-up months in the declared observation calendar. Other items retain a follow-up status and missing coverage value for subsequent review. Zero coverage represents a fully observed window with zero qualifying activity.

The observation calendar declares complete feed months. The local importer constructs a provisional calendar from source transaction months and records feed-completeness reconciliation as a business validation step.

`window_sensitivity.csv` also evaluates L through L+2. Each definition reports its own complete-item count and dollar total, providing a combined view of window and cohort sensitivity.

## Early sales and quantity

For complete-window items $I_c$, store $s$'s early net sales are:

$$EarlySales_s = \sum_{i \in I_c} \sum_{t \in W_i} Sales_{sit}.$$

`units_3m` applies the same calculation to billed quantity in the source billing unit. Currency parsing retains accounting negatives and returns, preserving net billed activity.

For participation group $g$, mean early sales equal the sum of store totals divided by the number of roster stores labeled $g$. Zero-purchase roster stores contribute zero under the complete-feed assumption. Outputs report store counts, total dollars, and per-store means together.

The original first-checkpoint view used four participation families. The current implementation retains the source's seven detailed categories, enabling comparisons by the more specific program labels.

## Item adoption coverage

A store is active for an item when at least one month in $W_i$ has **positive net monthly billed quantity**. Source records are aggregated to store-item-month before this condition is evaluated.

$$Coverage_i = 100 \times \frac{\#\{s: \exists t\in W_i, Quantity_{sit}>0\}}{\#\{\text{declared eligible roster stores}\}}.$$

The denominator uses the declared roster, including zero-purchase stores, under a common item-eligibility assumption. This produces a purchase-based distribution measure. An item-store eligibility table with effective dates is the next refinement for assortment, division availability, and store openings or closures.

The monthly-net activity rule incorporates purchases and returns within the same month. The original row-level rule evaluated positive underlying records. The two rules describe distinct operational definitions, and the current contract makes the chosen definition explicit.

## Source cumulative m12 outcome

The second checkpoint supplied `cum_sales_m12`, preserved here as `sales_m12`. The local arithmetic audit reconciles it to the sum of supplied `sales_m1` through `sales_m12`.

The model target is **source-indexed m12 cumulative sales**. Launch-calendar reconciliation is a separate next-stage task for defining a launch-aligned twelve-month outcome. The local execution workflow reads this cumulative field directly from the final source workbook.

The log-outcome model uses nonnegative cumulative values. Diagnostics count records outside that eligibility rule. Monthly returns remain part of early net-sales calculations, and the loader validates the completeness and numeric format of supplied values.

## OLS interaction regression by brand and division

The regression analysis uses `log(1 + source_m12_sales)` as the dependent variable. Program participation, brand, and division enter as categorical variables. The original project estimated these specifications separately:

```text
log(1 + source_m12_sales) ~ C(program) * C(brand)
log(1 + source_m12_sales) ~ C(program) * C(division)
```

Each specification includes the main effects of program and segment, plus program-by-segment interaction terms. The interaction terms describe how the program association varies across brands or divisions. Ordinary least squares (OLS) estimates the model coefficients.

Both use `None` as the program reference and conventional OLS standard errors. Their analytical scope is unadjusted association within the selected brand or division dimension, using static participation labels.

The portfolio implementation estimates a mean log outcome for each **observed, supported** program-segment cell:

$$\log(1+Y_{si}) = \mu_{g(s),h(si)} + \epsilon_{si}.$$

This is the observed-cell parameterization of a saturated interaction model. Model eligibility uses a configurable screening rule of at least **30 rows and five distinct stores** per cell. The support table retains cell counts and eligibility status for review. A planned pilot can add a dedicated power calculation based on its target effect and assignment unit.

Within segment $h$, the reported contrast is $\mu_{g,h}-\mu_{None,h}$. A contrast is estimated when both the program cell and its segment-specific baseline meet the support rule. This calculation combines the relevant cell means into the full within-segment comparison.

Store-clustered covariance, a small-sample correction, and t-based intervals account for repeated observations within stores. A joint Wald F-test evaluates equality of supported program-vs-`None` contrasts across segments, providing an association-heterogeneity test.

Outputs include pointwise 95% intervals, raw p-values, and Benjamini–Hochberg adjusted p-values within each moderator family. Interpret each interval and adjusted p-value alongside effect size and store support.

`exp(contrast)-1` gives the relative difference in the geometric mean of **1 + sales**. Separate support-table columns report arithmetic mean dollar sales. Each measure is interpreted on its specified scale.

## Participation labels

`None` represents known nonparticipation, and `Unknown` represents participation status awaiting classification. CSV parsing uses `keep_default_na=False` to preserve these distinct labels.

`AIM_Both` retains its literal source category. Its upstream coding definition is a business-reconciliation item. Combined AIM + One Source categories retain their separate labels. All observed categories appear in support tables, and the screening rule governs model eligibility.

## Analytical scope and development

The current models summarize program-group associations within brands or divisions. The next stage adds store characteristics, product controls, exposure timing, pre-period outcomes, and matched follow-up windows. Launch cadence, introductory discounts, and brand-specific auto-shipping eligibility provide additional business context for that specification.

A controlled or randomized pilot can extend this framework to incremental program evaluation. Product-level dependence can be addressed through an appropriate additional clustering or hierarchical specification as the study design develops.
