# Scope, joins and metric definitions

## Business question

Which product categories and destinations drive delivered sales, and where
should a marketplace team investigate delivery experience first?

Commercial scope is `order_status == 'delivered'`. All order statuses remain in
the source audit. This is a choice for a completed-order analysis; it excludes
cancelled, unavailable and unresolved orders rather than assuming their value
was earned. No accounting revenue-recognition policy is implied.

## Data model

| Table | Grain | Join / treatment |
|---|---|---|
| Orders | One order | Spine of the order view; unique `order_id` |
| Customers | One order-specific customer record | Unique `customer_id`; `customer_unique_id` links observed repeat purchases |
| Items | One item position within an order | Composite key: `order_id`, `order_item_id`; aggregate before order-level joins |
| Payments | One payment sequence within an order | Composite key: `order_id`, `payment_sequential`; aggregate before order-level joins |
| Reviews | One source review record | Neither review ID nor order ID is assumed unique; choose one answered review per order |
| Products | One product | Unique `product_id`; attach category to item rows |
| Sellers | One seller | Unique `seller_id`; attach seller attributes to item rows |
| Translation | One translated Portuguese category | Preserve unknown or untranslated categories rather than dropping sales |
| Geolocation | One coordinate observation | Many rows per ZIP prefix, including repeated rows; profile only, no analytical join |

The order view joins customers and separately aggregated items/payments/reviews
with `validate='one_to_one'`. The item view joins dimensions with
`validate='many_to_one'`. A failing assumed key stops the run instead of being
silently deduplicated.

Geolocation is intentionally unused in calculations. A nearest-carrier or
distance analysis would need additional cleaning and a stated spatial method;
it adds little to the state-level question here.

## Metrics

| Metric | Definition / denominator |
|---|---|
| Product sales | Sum of item `price` for delivered orders; BRL; excludes freight |
| Product AOV | Delivered product sales / delivered orders |
| Freight value | Sum of delivered-item `freight_value`; distinct from product sales |
| Payment value | Sum of all payment rows belonging to delivered orders; not profit or commission revenue |
| Eligible delivery | Delivered status; purchase, actual and estimated timestamps present; actual not before purchase; estimated calendar date not before purchase date |
| Late delivery | Actual calendar date strictly after estimated calendar date |
| Late rate | Late orders / eligible deliveries; unknown dates excluded |
| Delivery days | Actual delivery minus purchase timestamp, in fractional days; eligible deliveries only |
| Review comparison | Eligible deliveries with the selected review score in 1–5 |
| Low score | Selected review score is 1 or 2; denominator is eligible reviewed orders in the delivery group |
| Repeat customer | A `customer_unique_id` with more than one distinct delivered order anywhere in the extract |
| Observed repeat-customer rate | Repeat customers / distinct delivered-order customers; unequal follow-up windows, descriptive only |
| Cohort | Month of first observed delivered purchase; only cohorts from Jan 2017 are displayed |
| Cohort repeat rate at month k | Distinct cohort customers with a delivered purchase in month k / original cohort size; not cumulative |
| Seller concentration | Sellers ranked by delivered product sales; take the top `ceil(0.20 × seller_count)` |
| Seller late rate | Late seller-order combinations / eligible seller-order combinations; each seller-order once |

## Cleaning decisions

- Raw files are not overwritten. Date parsing raises for malformed non-empty
  values. Supplied timestamps are timezone-naive; no UTC assumption is added.
- Missing review text is optional feedback, not a missing score. It is profiled
  but not imputed or used for sentiment analysis.
- Latest `review_answer_timestamp` wins per order. Ties use creation timestamp,
  review ID and stable source order. The earliest answered review is a
  sensitivity check, not a second headline.
- Missing amounts are not set to zero. One delivered order lacks a payment
  record; payment totals represent available records.
- Item sales and payments are not interchangeable. Small rounding differences
  and larger source discrepancies are preserved. A diagnostic counts delivered
  orders with an absolute difference above R$0.05; no refund explanation is
  assumed without a refund ledger.
- Missing category is labelled `unknown`. Non-null categories without English
  translation retain the Portuguese name with an `untranslated:` prefix.
- Source geolocation duplicates remain in the raw file because no geographic
  join is needed. Other unique-key assumptions are checked explicitly.

## Boundaries and uncertainty

Commercial totals include every delivered order in the extract. The monthly
chart displays Jan 2017–Aug 2018; sparse 2016 edge months remain in CSV totals.
The closing extract can underrepresent late delivered purchases, particularly
August 2018. Changes are descriptive and are not used to forecast growth.

Cohorts use a conservative purchase cutoff of 31 July 2018. First purchases
are calculated from all delivered purchases up to the cutoff, including 2016,
before selecting displayed cohorts. A prior buyer is not relabelled as new in
January. The first observed purchase may still not be the customer's true first
purchase before the extract. Recent cohorts have less follow-up: these cells
remain blank, while observed months without a repeat purchase are zero.

The cohort view describes delivered purchases in the sample. It excludes
cancelled/unresolved purchases, purchases outside the source marketplaces, and
any history outside the extract. It is not a lifetime churn estimate.

Wilson 95% intervals are used for low-score proportions. They assume independent
binomial observations and do not resolve nonresponse bias or confounding.
Repeated customers and shared sellers can create dependence. The large
review-score gap is an association, not an estimated intervention effect.

Seller delivery outcomes are measured at order level. Multi-seller orders can
contribute the same outcome to more than one seller, so seller order counts are
not additive and cannot establish responsibility for a delay. Comparing low
volume seller/state rates requires care; the state chart uses a 100-eligible-
delivery minimum and seller tables retain denominators for filtering.

No supplied cost, margin, commission, carrier or experiment fields support a
profit calculation, carrier ranking, causal explanation or realised savings.
