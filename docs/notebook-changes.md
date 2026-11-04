# Notebook execution editions and source preservation

[Project overview](../README.md) · [Notebook guide](../notebooks/README.md)

The repository preserves the supplied analytical source in `notebooks/archive/` and provides execution editions in the parent notebook directory. All public notebooks have clean saved-output state. The source manifest records archive and active code hashes.

## Course transformation reference

The course reference retains its supplied source and demonstrates the wide-to-long operation. It remains identified as course material.

## Checkpoint 1 execution edition

The analytical sequence follows the source workflow: store participation, sales and launch joins, product mapping, early metrics, item coverage, and the final analytical join.

| Area | Execution edition |
|---|---|
| Local input | Reads the five canonical tables produced by the workbook importer |
| Participation | Uses the final static snapshot and derives the four participation families for the roster view |
| Product mapping | Uses the final validated item mapping; accepted launch dates define early-KPI eligibility |
| Runtime setup | Configures imports, paths, consistent variable names, and local output files |
| Joins | Applies one-to-one and many-to-one validation; joins item coverage on item and launch-cohort keys |
| Window | Calculates L+1 through L+3 with calendar periods and complete-follow-up flags |
| Denominator | Uses the declared master roster, including zero-purchase stores |
| Coverage | Applies positive net monthly quantity and retains zero coverage for fully observed items |
| Reconciliation | Checks independently calculated dollar totals and coverage against shared metric functions |

These are documented execution and metric enhancements made during portfolio preparation. Original report charts retain the source report's analytical version. The execution edition uses the normalized-data version and rules recorded here and in the import audit.

## Checkpoint 2 execution edition

The execution edition retains the original dependent-variable transformation, seven program categories, model formulas, standard-error specification, and plotting sequence. Imports are loaded before input reading; `AWG_SOURCE_DIR` selects the original workbook directory. Explicit parsing preserves the literal `None` category. The validation run checks the source sample size and rounded model R² values.

The separate Python package contains the supplementary support screening, store-clustered inference, and joint tests described in the methodology. The source OLS notebook and supplementary package have their respective specifications documented.

## Local execution

```bash
python scripts/check_notebooks.py --execute \
  --source /path/to/local/workbooks \
  --normalized /path/to/private/normalized \
  --output /path/to/private/notebook-validation
```

The command supplies `AWG_SOURCE_DIR`, `AWG_NORMALIZED_DIR`, and `AWG_OUTPUT_DIR`, executes the active editions, and writes executed notebooks and client outputs to the separate local directory. The public source notebooks remain clean.
