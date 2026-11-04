# Analytical design decisions

[Repository home](../README.md)

The portfolio implementation extends the original client analysis with explicit data contracts, reusable code, and documented local execution.

| Analytical objective | Implementation decision | Practical value |
|---|---|---|
| Preserve transformation work | Retain the original course reference and checkpoint source | Traceable transformation logic and analytical history |
| Support fresh execution | Package functions and notebooks with declared dependencies | Reproducible execution from a clean environment |
| Align units of analysis | Define monthly store-item, cumulative store-item, and store-summary grains | Metrics interpreted at the appropriate level |
| Maintain join integrity | Validate unique dimension keys and many-to-one joins | Controlled row counts and aggregate totals |
| Preserve item-level adoption | Deliver item coverage as a standalone result table | Coverage retains its intended item grain |
| Align follow-up periods | Use calendar periods for L+1 through L+3 | Consistent cross-year launch windows |
| Track cohort completeness | Store follow-up flags and coverage status | Clear eligibility for complete-window KPIs |
| Preserve supplied values | Parse numeric fields explicitly and classify participation status | Traceable measures and comparison groups |
| Make denominators explicit | Use a declared roster and common-eligibility assumption | Reviewable store counts including zero-purchase stores |
| Incorporate returns | Aggregate net monthly quantity before activity classification | Operationally defined adoption measure |
| Review launch events | Keep ambiguous dates and out-of-range years in a review file | Business confirmation preserves source traceability |
| Preserve cumulative outcomes | Use source-indexed m12 and document launch-calendar reconciliation | Clear outcome definition and development path |
| Estimate observed segment profiles | Fit means for supported observed cells | Direct within-segment contrasts |
| Evaluate independent support | Screen distinct stores and cluster intervals by store | Sample structure accompanies every comparison |
| Contextualize multiple comparisons | Provide BH-adjusted p-values per moderator family | Effect size, interval, and multiplicity reported together |
| Connect findings to decisions | Organize segment results into pilot priorities | Concrete next-stage program evaluation |
| Support local reproduction | Document required workbooks, input contracts, and local commands | Original project evidence and a clear execution path |

The source map records the original analytical materials. The [deliverables overview](project-deliverables.md) describes the completed client analysis and the later portfolio implementation.
