# Project code and local execution

[Repository home](../README.md)

## Original analysis notebooks

The [notebook directory](../notebooks/README.md) contains execution editions of both checkpoint analyses and the original course reference. The linked archive preserves supplied source code and cell order. All public saved outputs are cleared. The manifest and [change record](notebook-changes.md) document the source and execution editions.

The source archive records the historical Colab conventions and intermediate-file sequence. The active editions use configured local directories and provide a fresh execution path for preparation, KPIs, OLS models, and plots.

## Environment

Use Python 3.10 or later. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows activation: `.venv\Scripts\activate`. The package dependencies cover pandas, Excel reading, OLS regression, and plotting. `requirements-lock.txt` records the environment used for local validation on Python 3.13.

## Local client materials

Client data and generated tables use directories outside the public repository. The supplementary importer reads these source workbooks:

- `dv_dataset_with_all_program_info.xlsx`, sheet `dv_dataset_with_all_program_inf`
- `AWG All Store List 10.1.xlsx`
- `all_month.xlsx`
- `Sales_Data_Raw.xlsx`

The first-checkpoint source notebook also refers to AIM and One Source store lists, product classifications, and intermediate joined tables. Those historical steps are retained in the original notebook. The supplementary importer uses the final participation and product mappings to create the canonical input contract.

```bash
python scripts/prepare_private_data.py \
  --source /path/to/local/workbooks \
  --output /path/to/private/normalized

awg-analyze \
  --data /path/to/private/normalized \
  --output /path/to/private/results \
  --label 'LOCAL PROJECT ANALYSIS'
```

Both analysis paths and result paths are supplied explicitly. The pipeline writes client results to the separate local directory.

## Execute the project notebooks

After preparing normalized inputs, run:

```bash
python scripts/check_notebooks.py --execute \
  --source /path/to/local/workbooks \
  --normalized /path/to/private/normalized \
  --output /path/to/private/notebook-validation
```

The command supplies all notebook input settings and writes executed copies and local results to the selected private output directory. The course reference runs its original transformation exercise. The first-checkpoint edition reconciles its calculated totals and coverage with the shared functions; the second-checkpoint edition retains the original OLS formulas and checks source counts and rounded R².

## Supplementary workflow

The importer validates store-item outcome grain and dimension consistency, deduplicates identical master keys, and preserves the final static participation snapshot. Master stores awaiting classification receive `Unknown`. The final workbook supplies the product mapping.

Accepted launch dates are unambiguous dates in the documented 2024–2025 range. The launch review file preserves other dates for business confirmation. Source m12 outcomes retain their original population, and accepted launch dates determine early-KPI eligibility.

The import audit records fiscal/calendar interpretation, feed completeness, common item-store eligibility, participation timing, product mappings, and source month indexing. The pipeline produces eight result tables, three figures, a written summary, and input hashes. The [methodology](methodology.md) and [design decisions](decision-log.md) describe the supplementary implementation and its relationship to the original analysis.

## Validation

```bash
python -m pytest -q
python scripts/check_notebooks.py
python scripts/validate_repository.py
```

The tests cover metric and regression behavior. The notebook check validates file structure, active Python syntax, archive/active hashes, and clean public source state. Its `--execute` option runs the active notebooks against local client files. Full data execution uses the local client workbooks and the paths supplied above. Repository checks validate required artifacts, local documentation links, and the separation of client data from public files.

## Public packaging

```bash
python scripts/export_public.py --output /path/outside/repository/awg-program-participation.zip
```

The exporter packages an explicit set of project code, documentation, and report-image files. Client workbooks and generated analysis tables remain in their local directory. GitHub publication is a separate repository-management step.
