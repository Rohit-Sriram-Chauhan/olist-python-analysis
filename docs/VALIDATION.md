# Validation record

Checked on 8 November 2026 (India time), using Python 3.12.14, pandas 2.2.3,
NumPy 2.3.5 and Matplotlib 3.10.8.

## Execution

- `python run_analysis.py` completed on the supplied nine source files.
- All 20 code cells in the 40-cell notebook were executed sequentially in one
  Python namespace. Saved outputs include actual DataFrames and six chart
  images; no placeholder results are used.
- The notebook is nbformat 4.4. Its execution counts, rich-output types and
  absence of error outputs were checked. Cell execution used a plain-Python
  runner because Jupyter was unavailable in the build environment; the
  interactive Jupyter interface itself was not tested there.
- Six exported charts were visually reviewed for labels, readable numbers and
  clipping. The HTML report was checked for complete embedded images and valid
  local project links. A browser layout render was not available in the build
  environment; the responsive report uses standard HTML/CSS.

## Ten source reconciliation checks

These are computed in `src/analysis.py`, written to
`outputs/tables/validation_checks.csv`, and stop the run if a check fails.

1. Exactly one order-view row for every original order.
2. Item-view row count unchanged.
3. Delivered product sales equal an independent raw-item sum.
4. Delivered payment value equals an independent raw-payment sum.
5. Category sales reconcile to raw delivered-item sales.
6. Monthly sales reconcile to raw delivered-item sales.
7. State sales reconcile to raw delivered-item sales.
8. All delivered orders have item totals.
9. Review groups cover exactly the eligible reviewed deliveries.
10. Unknown delivery outcomes remain unclassified rather than becoming on time.

Money comparisons use an absolute R$0.01 tolerance and zero relative tolerance.
This verifies source reconciliation, not that payment and item values must
match each other. Counts and identifiers are checked exactly.

## Eight synthetic tests

Run `python -m unittest discover -s tests -v`. All eight tests passed.

- Several item/payment/review rows on one order do not multiply its money.
- Arrival after midnight on the estimated date remains on time.
- Missing actual delivery is unknown, with no fabricated duration.
- Latest and earliest review policies select the intended rows.
- A duplicated product key raises an error rather than silently dropping data.
- A missing payment record stays missing.
- Cohorts distinguish observed zero returns from unobserved future months.
- Wilson intervals handle empty groups and proportions of zero or one.

## Additional package checks

The distributed packages are checked for archive integrity, required files,
relative Markdown links, source-file hashes and raw-data exclusion from the
GitHub-ready package. Source CSVs are unmodified. The raw data, notebook,
summary tables and report are reproducible locally using the included script.

The package does not claim that the optional Jupyter dependency range was
installed in this build environment or that it was tested on Windows. The
analysis runtime is pinned; a compatible local Python installation and network
access are needed to install packages on a new computer.
