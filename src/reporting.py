"""Write a portable HTML report and a concise Markdown business summary."""

import base64
from html import escape
from pathlib import Path


def create_report(tables, metrics, figures, path):
    path = Path(path)
    m = metrics
    review = tables["delivery_reviews"]
    states = tables["state_performance"]
    diagnostics = tables["quality_diagnostics"].set_index("check")["count"]
    top_state = states.index[0]
    top_state_row = states.iloc[0]
    core = tables["monthly_sales"].loc["2017-01":"2018-08"]
    peak_month = str(core["product_sales"].idxmax())
    gap = m["late_low_score_pct"] - m["on_time_low_score_pct"]
    low_ratio = m["late_low_score_pct"] / m["on_time_low_score_pct"]

    summary = f"""# Olist marketplace performance review

## Decision to investigate
Start with delivery operations in high-volume destinations. Late deliveries are
associated with much poorer reviews, although this analysis does not establish
that lateness alone caused the difference.

## Scope and results
- Historical extract: {m['all_purchase_start'][:10]} to {m['all_purchase_end'][:10]} (all order purchases).
- {m['raw_orders']:,} source orders; {m['delivered_orders']:,} delivered orders used for commercial analysis.
- Product sales: **R$ {m['product_sales_brl']:,.2f}**, excluding freight. This is merchandise value, not Olist's revenue or profit.
- Product-only average order value: **R$ {m['product_aov_brl']:,.2f}**.
- Late rate: **{m['late_rate_pct']:.2f}%** ({m['late_orders']:,} / {m['eligible_deliveries']:,} eligible deliveries).
- Average review: **{m['on_time_review_score']:.2f}/5 on time** versus **{m['late_review_score']:.2f}/5 late**.
- Low scores (1–2 stars): **{m['on_time_low_score_pct']:.1f}% on time** versus **{m['late_low_score_pct']:.1f}% late**; a **{gap:.1f} percentage-point** descriptive gap.
- Largest category by product sales: **{m['top_category']}**, R$ {m['top_category_sales_brl']:,.2f}.
- Highest product-sales month in the displayed Jan 2017–Aug 2018 window: **{peak_month}**. This does not identify the cause of the peak.
- **{top_state}** has the largest late-order count ({int(top_state_row['late_orders']):,}), with a {top_state_row['late_rate_pct']:.2f}% late rate. Volume and rate should be reviewed together.
- The top 20% of delivered-order sellers account for **{m['top_20pct_sellers_sales_pct']:.1f}%** of product sales.
- **{m['observed_repeat_customer_pct']:.2f}%** of observed delivered-order customers purchased more than once ({m['repeat_customers']:,} / {m['unique_delivered_customers']:,}). This is not a lifetime retention or churn estimate.

## Suggested actions and how to assess them
1. Audit carrier handoff, transit and promised dates in the high-volume late-delivery destinations. Track late-order count, rate and median delivery time weekly; investigate before assigning responsibility.
2. Trial proactive updates for at-risk orders. Compare low-score rates in a controlled pilot; do not treat the historical association as a forecast of improvement.
3. Review service coverage for high-sales sellers. Seller metrics count each seller-order once, but delivery is measured for the whole order; multiple sellers can share the same outcome.
4. Use cohort findings to design a small repeat-purchase test. Keep equal follow-up windows and compare incremental repeat purchasing with a control group.

## Data decisions that affect interpretation
- Aggregate item and payment rows separately before joining to one row per order. Category sales remain at item grain.
- Select the latest answered review per order, with stable tie-breakers. The earliest-review alternative is exported as a sensitivity check.
- An arrival on the estimated calendar date counts as on time. {int(diagnostics['delivered_without_valid_delivery_dates'])} delivered orders lack valid dates and are excluded from delivery-rate denominators.
- Reviews use eligible deliveries with a valid score only: on time n={int(review.loc['On time', 'reviewed_orders']):,}, late n={int(review.loc['Late', 'reviewed_orders']):,}.
- Payments include freight and can differ from item price plus freight. {int(diagnostics['delivered_payment_difference_over_005_brl']):,} delivered orders differ by more than R$0.05; amounts are preserved rather than forced to match.
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
"""
    path.with_name("executive_summary.md").write_text(summary, encoding="utf-8")

    def image(number, alt):
        file = next(p for p in figures if p.name.startswith(f"{number:02d}_"))
        encoded = base64.b64encode(file.read_bytes()).decode("ascii")
        return f'<img alt="{escape(alt)}" src="data:image/png;base64,{encoded}">'

    def table_html(df):
        labels = {"reviewed_orders": "Reviewed orders", "average_score": "Avg score / 5",
                  "low_score_rate_pct": "Low scores (%)", "ci_low_pct": "95% lower (%)",
                  "ci_high_pct": "95% upper (%)"}
        display_table = df.rename(columns=labels).rename_axis("Delivery group")
        return display_table.to_html(classes="data", border=0, float_format=lambda x: f"{x:,.2f}")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Olist | Marketplace performance review</title>
<style>
:root{{--navy:#17324d;--teal:#16897f;--coral:#d86b52;--muted:#60738a;--line:#dfe6ec;--paper:#fff;--bg:#f2f5f7}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--navy);font:16px/1.65 system-ui,-apple-system,'Segoe UI',sans-serif}}
main{{max-width:1180px;margin:auto;padding:44px 30px 60px}}header{{padding:44px;border-radius:18px;background:var(--navy);color:white}}
.eyebrow{{font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:#92d9d1}}
h1{{font-size:clamp(30px,4vw,46px);line-height:1.15;max-width:900px;margin:16px 0 20px;letter-spacing:-.035em}}
header p{{color:#dae5f0;max-width:880px;margin-bottom:0}}h2{{font-size:27px;line-height:1.25;margin:0 0 15px;letter-spacing:-.02em}}
h3{{font-size:18px;margin:0 0 10px}}p{{margin:0 0 16px}}a{{color:var(--teal)}}.subtle{{font-size:13px;color:var(--muted)}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:24px 0}}
.metric{{background:white;border:1px solid var(--line);border-radius:12px;padding:22px}}
.metric strong{{display:block;font-size:29px;line-height:1.3;margin:10px 0 4px;font-variant-numeric:tabular-nums}}
.metric span{{font-size:13px;color:var(--muted)}}section{{background:white;border:1px solid var(--line);border-radius:14px;margin:22px 0;padding:32px}}
.section-no{{font-size:12px;color:var(--teal);font-weight:800;letter-spacing:.12em;display:block;margin-bottom:10px}}
img{{display:block;max-width:100%;width:100%;height:auto;margin:22px 0 12px}}.caption{{font-size:13px;color:var(--muted)}}
.callout{{border-left:4px solid var(--teal);background:#eef7f5;padding:18px 22px;border-radius:0 8px 8px 0;margin:20px 0}}
.columns{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}.scroll{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}}
th,td{{padding:10px 12px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}}th:first-child,td:first-child{{text-align:left}}thead{{background:#eff4f6}}
li{{margin-bottom:10px}}footer{{font-size:12px;color:var(--muted);padding:12px 4px}}.pill{{display:inline-block;padding:3px 10px;background:#e5f3ef;color:var(--teal);font-size:12px;border-radius:20px;margin-bottom:14px}}
@media(max-width:760px){{main{{padding:16px}}header,section{{padding:23px}}.metrics{{grid-template-columns:repeat(2,1fr)}}.columns{{grid-template-columns:1fr}}.metric{{padding:16px}}.metric strong{{font-size:25px}}}}
@media print{{body{{background:white}}main{{max-width:none;padding:0}}section{{break-inside:avoid;border-radius:0}}header{{border-radius:0}}img{{max-height:650px;object-fit:contain}}}}
</style></head><body><main>
<header><div class="eyebrow">Python portfolio · Olist · historical data, 2016–2018</div>
<h1>Marketplace performance review</h1>
<p>Where do sales come from, and which service issues deserve attention? An analysis of orders, items, payments, customers and delivery experience.</p></header>
<div class="metrics">
<div class="metric"><span>PRODUCT SALES</span><strong>R$ {m['product_sales_brl']/1e6:.2f}m</strong><span>Delivered orders · excludes freight</span></div>
<div class="metric"><span>DELIVERED ORDERS</span><strong>{m['delivered_orders']:,}</strong><span>Of {m['raw_orders']:,} source orders</span></div>
<div class="metric"><span>LATE DELIVERY RATE</span><strong>{m['late_rate_pct']:.2f}%</strong><span>{m['late_orders']:,} / {m['eligible_deliveries']:,} eligible</span></div>
<div class="metric"><span>OBSERVED REPEAT BUYERS</span><strong>{m['observed_repeat_customer_pct']:.2f}%</strong><span>Customers with 2+ delivered orders</span></div>
</div>
<section><span class="section-no">THE DECISION</span><h2>Start with delivery reliability.</h2>
<p>Late deliveries are a minority of orders, but their review scores are much lower. The first operational review should combine the number of late orders with the late rate, rather than ranking destinations on one metric alone.</p>
<div class="callout"><strong>On-time orders average {m['on_time_review_score']:.2f}/5; late orders average {m['late_review_score']:.2f}/5.</strong><br>
This is a descriptive relationship. Product mix, location, seller performance and review selection can also affect the comparison.</div>
<p class="subtle">Commercial scope: delivered orders across the extract. Currency: Brazilian real (BRL). Product sales represent item price, not marketplace revenue or profit. No performance claim is made about Olist today.</p></section>
<section><span class="section-no">01 / COMMERCIAL PERFORMANCE</span><h2>Establish the sales baseline.</h2>
<p>Delivered orders generated R$ {m['product_sales_brl']:,.2f} in product sales, with a product-only average order value of R$ {m['product_aov_brl']:,.2f}. The highest sales month in the displayed window is {peak_month}; the data alone do not explain why.</p>
{image(1, 'Monthly product sales and delivered order counts, January 2017 to August 2018')}
<p class="caption">Grouped by purchase month, not delivery month. Sparse 2016 edge months are omitted from this chart but retained in total sales. August 2018 can be affected by the closing observation window.</p>
{image(2, 'Top ten product categories ranked by product sales')}
<p class="caption">Category totals use item prices only. An order can contain several categories, so category order counts cannot be added together.</p></section>
<section><span class="section-no">02 / DELIVERY AND EXPERIENCE</span><h2>Balance exposure with service risk.</h2>
<p>{escape(top_state)} accounts for {int(top_state_row['late_orders']):,} late orders, the largest count, at a {top_state_row['late_rate_pct']:.2f}% late rate. The destinations below are the eight largest late-order counts among states with at least 100 eligible deliveries.</p>
{image(3, 'Late-order volume and rate by customer state')}
<div class="callout"><strong>Low reviews are {low_ratio:.1f} times as common among late orders.</strong><br>
The 1–2 star rate is {m['late_low_score_pct']:.1f}% for late orders and {m['on_time_low_score_pct']:.1f}% for on-time orders: a {gap:.1f} percentage-point gap.</div>
{image(4, 'Review scores and low-score proportions for late and on-time deliveries')}
<div class="scroll">{table_html(review[['reviewed_orders','average_score','low_score_rate_pct','ci_low_pct','ci_high_pct']])}</div>
<p class="caption">Low score = 1 or 2 stars. Eligible deliveries with a valid selected review only. Wilson intervals describe binomial uncertainty under independence assumptions; repeated customers and shared sellers may violate independence. They do not address confounding or review nonresponse. Earliest/latest review-policy comparisons are included in the output tables.</p></section>
<section><span class="section-no">03 / CUSTOMER DEPTH · OPTIONAL ADVANCED ANALYSIS</span><h2>Measure repeat purchasing with fair follow-up.</h2>
<p>{m['repeat_customers']:,} of {m['unique_delivered_customers']:,} observed customers placed more than one delivered order ({m['observed_repeat_customer_pct']:.2f}%). The cohort view gives each purchase group its own follow-up timeline.</p>
{image(5, 'Cohort repeat-purchase percentages, excluding month zero')}
<p class="caption">Rows are first observed delivered-purchase months. A customer is counted once in each later month with a delivered purchase. Rates are not cumulative; the same customer may return in several months. Month 0 is 100% by definition and omitted. Grey cells are unobserved, not zero. Cutoff: 31 July 2018.</p>
<p>Use this to design a repeat-purchase pilot, not to label all one-time customers as churned. The marketplace extract has a limited window and does not capture a customer's purchases outside the dataset.</p></section>
<section><span class="section-no">04 / SELLER CONCENTRATION</span><h2>Prioritise service coverage where sales are concentrated.</h2>
{image(6, 'Cumulative product sales by sellers ranked from highest to lowest sales')}
<p>The top 20% of delivered-order sellers account for {m['top_20pct_sellers_sales_pct']:.1f}% of product sales. Reviewing service coverage for this group is a practical starting point. An order's delivery outcome can be shared by multiple sellers, so the analysis cannot identify who caused a delay.</p></section>
<section><span class="section-no">NEXT ACTIONS</span><h2>Turn findings into testable work.</h2><div class="columns">
<div><h3>Operations</h3><p>Review handoff, transit and promised dates in the largest late-order destinations. Track both late-order volume and rate weekly before assigning responsibility.</p><h3>Customer experience</h3><p>Trial proactive updates for at-risk orders. Use a controlled pilot to measure the change in low-review rates.</p></div>
<div><h3>Seller management</h3><p>Review service coverage for high-sales sellers. Use the exported seller table for investigation, with a minimum eligible-order threshold when comparing rates.</p><h3>Customer marketing</h3><p>Test a repeat-purchase offer with equal follow-up windows and a control group. Compare incremental repeat purchasing rather than raw campaign totals.</p></div></div>
<p class="subtle">These are proposed actions. The project does not claim realised savings, profit growth or an intervention effect.</p></section>
<section><span class="section-no">METHOD AND QUALITY</span><h2>Keep the numbers traceable.</h2>
<ul><li>Order items and payments are aggregated separately before joining. Order totals are never repeated across item rows.</li>
<li>The latest answered review is selected per order; ties use creation timestamp and review ID. A second selection policy is exported for comparison.</li>
<li>Same-calendar-day arrivals count as on time. {int(diagnostics['delivered_without_valid_delivery_dates'])} delivered orders have unusable delivery dates and are excluded from service-rate denominators.</li>
<li>One delivered order lacks a payment record. {int(diagnostics['delivered_payment_difference_over_005_brl']):,} delivered orders have a payment difference above R$0.05 versus item prices plus freight. Original values are preserved and the two monetary measures remain separate.</li>
<li>The geolocation file is profiled but not joined: it has multiple records per ZIP prefix, and state-level analysis already answers the business question.</li>
<li>Costs, refund-ledger entries, carrier identity and experiment assignment are unavailable. No margin or causal estimate is presented.</li></ul>
<p><strong>{len(tables['validation_checks'])} reconciliation checks passed.</strong> The project includes source-file hashes, missing-value counts, quality diagnostics, exported summary tables and synthetic edge-case tests.</p>
<p class="subtle">All purchase timestamps span {m['all_purchase_start'][:10]} to {m['all_purchase_end'][:10]}; delivered purchases span {m['delivered_purchase_start'][:10]} to {m['delivered_purchase_end'][:10]}. Timestamps are analysed as supplied, without an assumed timezone conversion.</p></section>
<footer>Source: <a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce">Brazilian E-Commerce Public Dataset by Olist</a> · Dataset and adapted data outputs: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>.<br>
Python portfolio project · pandas, NumPy and Matplotlib · All charts and tables computed from the supplied CSV files. Open this report offline; its images are embedded.</footer>
</main></body></html>"""
    path.write_text(html, encoding="utf-8")
