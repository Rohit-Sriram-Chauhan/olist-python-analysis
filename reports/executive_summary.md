# Olist marketplace performance review

## Decision to investigate
Start with delivery operations in high-volume destinations. Late deliveries are
associated with much poorer reviews, although this analysis does not establish
that lateness alone caused the difference.

## Scope and results
- Historical extract: 2016-09-04 to 2018-10-17 (all order purchases).
- 99,441 source orders; 96,478 delivered orders used for commercial analysis.
- Product sales: **R$ 13,221,498.11**, excluding freight. This is merchandise value, not Olist's revenue or profit.
- Product-only average order value: **R$ 137.04**.
- Late rate: **6.77%** (6,534 / 96,470 eligible deliveries).
- Average review: **4.29/5 on time** versus **2.27/5 late**.
- Low scores (1–2 stars): **9.3% on time** versus **62.4% late**; a **53.2 percentage-point** descriptive gap.
- Largest category by product sales: **health_beauty**, R$ 1,233,131.72.
- Highest product-sales month in the displayed Jan 2017–Aug 2018 window: **2017-11**. This does not identify the cause of the peak.
- **SP** has the largest late-order count (1,820), with a 4.49% late rate. Volume and rate should be reviewed together.
- The top 20% of delivered-order sellers account for **82.3%** of product sales.
- **3.00%** of observed delivered-order customers purchased more than once (2,801 / 93,358). This is not a lifetime retention or churn estimate.

## Suggested actions and how to assess them
1. Audit carrier handoff, transit and promised dates in the high-volume late-delivery destinations. Track late-order count, rate and median delivery time weekly; investigate before assigning responsibility.
2. Trial proactive updates for at-risk orders. Compare low-score rates in a controlled pilot; do not treat the historical association as a forecast of improvement.
3. Review service coverage for high-sales sellers. Seller metrics count each seller-order once, but delivery is measured for the whole order; multiple sellers can share the same outcome.
4. Use cohort findings to design a small repeat-purchase test. Keep equal follow-up windows and compare incremental repeat purchasing with a control group.

## Data decisions that affect interpretation
- Aggregate item and payment rows separately before joining to one row per order. Category sales remain at item grain.
- Select the latest answered review per order, with stable tie-breakers. The earliest-review alternative is exported as a sensitivity check.
- An arrival on the estimated calendar date counts as on time. 8 delivered orders lack valid dates and are excluded from delivery-rate denominators.
- Reviews use eligible deliveries with a valid score only: on time n=89,443, late n=6,381.
- Payments include freight and can differ from item price plus freight. 256 delivered orders differ by more than R$0.05; amounts are preserved rather than forced to match.
- Cohorts use first observed delivered purchase; the conservative purchase cutoff is 31 Jul 2018. Grey cells are not observable; zero cells are observed with no later purchase.
- The trend chart omits sparse 2016 edge months. August 2018 delivered-order results may be affected by the extract's closing window. No seasonal or growth forecast is claimed.
- No cost, margin, carrier identity, refund ledger or experiment assignment is supplied. No profit, causal effect or realised savings is estimated.
- The data are historical; these are portfolio findings, not a description of Olist today.

## Reproduce and inspect
Run `python run_analysis.py`. See `outputs/tables/validation_checks.csv` for
source reconciliation checks, `outputs/tables/quality_diagnostics.csv` for issues,
and the notebook for the analysis walkthrough.

Source: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
Dataset and adapted data outputs: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
