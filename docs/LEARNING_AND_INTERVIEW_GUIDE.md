# Learn the project and explain it clearly

## Start with a short explanation

Use this once you have run the project and can explain the calculations:

> I analysed Olist's historical marketplace data to understand sales and
> delivery experience. The main technical challenge was joining tables with
> different levels of detail without multiplying totals. I created separate
> order and item views, checked totals against the raw files, and found that
> late orders had much lower reviews. I recommended an operational review and
> a controlled communication pilot, while keeping the finding descriptive.

Do not memorise only the numbers. Be ready to show one join, one calculation,
one chart and one limitation in the notebook.

## Study order

| Level | What to understand | Where to practise |
|---|---|---|
| Core | Load CSVs, inspect rows and missing values | Notebook: source audit |
| Core | Filter delivered orders; distinguish a row from an order | `prepare_data` and notebook scope section |
| Core | `groupby`, named aggregation and safe `merge` | `prepare_data`, `monthly_sales`, `category_sales` |
| Core | Dates, nulls and Boolean conditions | `add_delivery_features` |
| Core | Compare groups and write a business interpretation | `delivery_reviews` and the report |
| Intermediate | Reconcile source totals and test edge cases | `validate_results`, `tests/test_analysis.py` |
| Optional advanced | Cohorts, sparse follow-up and repeat purchasing | `cohort_retention` |
| Optional advanced | Seller concentration and uncertainty intervals | `seller_performance`, `wilson_interval` |

The core project is already useful without a machine-learning model. A model
would need a separate prediction question, a prediction-time feature audit,
a time-based split and an operational evaluation plan.

## Interview questions and answer points

### 1. What does one row mean?
In the order view, one row is one order. In the item view, one row is one item
position within an order. A payment row is a payment sequence, not an order.

### 2. Why not merge all CSVs immediately?
An order with two items and two payments would produce four rows in a direct
join. Summing prices or payments after that can double totals. Aggregate each
one-to-many table first; check `merge(validate=...)` and reconcile to source.

### 3. How did you calculate sales and AOV?
Product sales are the sum of item prices belonging to delivered orders. Product
AOV divides those sales by delivered orders. Freight is separate. These values
are not Olist's commissions, accounting revenue or profit.

### 4. What did you do with missing values?
Keep raw data unchanged. Missing review comments are optional text and are not
used. Missing delivery dates exclude an order from delivery comparisons but
not from sales. Missing money stays unknown rather than becoming zero.

### 5. How did you decide an order was late?
Compare actual and estimated calendar dates, after checking that dates are
available and sensible. An arrival at 8 pm on the promised date is on time even
though it is later than the estimate's midnight timestamp.

### 6. Why choose the latest review?
Some orders have several review rows. One consistent policy preserves an
order-level comparison. The latest answered review is the main policy; the
earliest answered review is exported as a sensitivity check. The average-score
conclusion barely changes between these policies in this extract.

### 7. Does delivery delay cause poor reviews?
This analysis cannot establish that. Product mix, customer location and other
factors can affect both. The result motivates investigation and a controlled
pilot rather than a claimed improvement from fixing delays.

### 8. Why not call the 3% repeat rate a retention rate?
The simple figure is observed repeat purchasing over unequal windows. It is
not lifetime retention. Cohorts compare customers by time since first observed
purchase, keep denominators fixed and leave future periods unobserved.

### 9. Why use `customer_unique_id`?
Olist uses a different `customer_id` for each order-specific customer record.
`customer_unique_id` connects observed purchases by the same customer. Using
the order-specific ID would make repeat purchasing disappear.

### 10. What do the confidence intervals mean?
They are Wilson intervals around low-score proportions, under binomial
independence assumptions. They illustrate proportion uncertainty but do not
fix review nonresponse, seller/customer dependence, or confounding.

### 11. How did you check that the results were correct?
Validate join keys and cardinality, preserve row counts, and compare sales and
payments with independent raw-table totals. Eight small tests also check
multi-row joins, same-day delivery, missing dates, review selection and cohorts.

### 12. What would you ask the business for next?
Carrier and handoff details, promised-date change history, costs/commissions,
refund records and an intervention assignment table. These would support a
more specific operational or financial question.

## Three exercises to make your own contribution

### Exercise A — Payment mix (core)

Question: which payment methods account for the largest share of recorded
payment value on delivered orders?

Start from payment rows. Filter them with `order_id.isin(delivered.order_id)`,
then group by `payment_type` and sum `payment_value`. Verify that the grouped
total equals the raw delivered-payment total. Do not count payment rows as
orders. Explain how split payments affect the interpretation.

### Exercise B — Delivery time by state (intermediate)

Question: do the states with the highest median delivery time also have the
highest late rate?

Use `delivery_days` and `state_performance`. Filter to at least 100 eligible
deliveries, compare both metrics, and explain how different delivery promises
can make a long delivery on time. Make one scatter plot and write three
sentences about it.

### Exercise C — Equal-window repeat purchasing (advanced)

Question: what share of customers buy again within 90 days of their first
observed delivered purchase?

Use a fixed observation cutoff of 31 July 2018. Keep only customers whose first
observed delivered purchase is at least 90 days before that cutoff. Count a
second distinct delivered order in the next 90 days; do not include same-order
item rows. Compare the result with the all-window 3% repeat figure and explain
why the denominators differ. It still does not estimate lifetime churn.

Keep your answer, assumptions and a validation check in the notebook's final
section. Add the result to the README only after running and understanding it.

## Resume wording to adapt after practising

- Analysed 99,441 Olist orders using Python, pandas and Matplotlib, building
  order- and item-level views with source reconciliation checks.
- Evaluated R$13.22M in delivered product sales and delivery-review differences;
  added cohort repeat-purchase analysis and documented business recommendations.

These bullets describe a portfolio analysis. Do not add invented experience,
implemented savings or a percentage improvement that was never measured.
