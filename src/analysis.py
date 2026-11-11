"""Olist analysis: preserve each table's grain before combining it with orders.

Amounts are BRL. Product sales exclude freight and are not marketplace revenue
or profit. All commercial summaries use delivered orders unless stated otherwise.
"""

from pathlib import Path
from statistics import NormalDist
import hashlib

import numpy as np
import pandas as pd


FILES = {
    "orders": "olist_orders_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "translation": "product_category_name_translation.csv",
    "geolocation": "olist_geolocation_dataset.csv",
}

DATE_COLUMNS = {
    "orders": ["order_purchase_timestamp", "order_approved_at",
               "order_delivered_carrier_date", "order_delivered_customer_date",
               "order_estimated_delivery_date"],
    "items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}


def load_data(data_dir):
    """Read the original nine files. Fail clearly if a required file is absent."""
    data_dir = Path(data_dir)
    missing = [name for name in FILES.values() if not (data_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing files in {data_dir}: {', '.join(missing)}")
    raw = {}
    for name, filename in FILES.items():
        # String ZIP prefixes preserve leading zeros; identifiers are not numbers.
        raw[name] = pd.read_csv(data_dir / filename, dtype={
            "customer_zip_code_prefix": "string",
            "seller_zip_code_prefix": "string",
            "geolocation_zip_code_prefix": "string",
        })
        for col in DATE_COLUMNS.get(name, []):
            # A malformed non-empty timestamp raises instead of disappearing.
            raw[name][col] = pd.to_datetime(raw[name][col], errors="raise")
    return raw


def profile_data(raw):
    """Return file-level inventory and field-level missingness, without editing raw."""
    inventory, missing = [], []
    for name, df in raw.items():
        inventory.append({"table": name, "rows": len(df), "columns": len(df.columns),
                          "exact_duplicate_rows": int(df.duplicated().sum())})
        for col in df:
            n = int(df[col].isna().sum())
            missing.append({"table": name, "column": col, "missing_rows": n,
                            "missing_pct": 100 * n / len(df)})
    return pd.DataFrame(inventory), pd.DataFrame(missing)


def check_unique(df, columns, name):
    """Stop rather than silently deduplicating an assumed key."""
    if df[columns].isna().any().any() or df.duplicated(columns).any():
        raise ValueError(f"{name}: expected non-null unique key {columns}")


def select_reviews(reviews, keep="last"):
    """One review per order: latest response, with deterministic tie-breakers.

    review_id is not assumed to be unique. `keep='first'` supports a sensitivity
    check without changing the main latest-response policy.
    """
    return (reviews.sort_values(
        ["order_id", "review_answer_timestamp", "review_creation_date", "review_id"],
        kind="stable", na_position="first")
        .drop_duplicates("order_id", keep=keep)
        [["order_id", "review_score"]])


def add_delivery_features(orders):
    """Keep unknown delivery outcomes nullable; compare promised calendar dates."""
    orders = orders.copy()
    purchased = orders["order_purchase_timestamp"]
    actual = orders["order_delivered_customer_date"]
    estimated = orders["order_estimated_delivery_date"]
    valid = (orders["order_status"].eq("delivered") & purchased.notna()
             & actual.notna() & estimated.notna() & actual.ge(purchased)
             & estimated.dt.normalize().ge(purchased.dt.normalize()))
    orders["delivery_eligible"] = valid
    orders["delivery_days"] = ((actual - purchased).dt.total_seconds() / 86400).where(valid)
    # Estimated dates are midnight values. Same-calendar-day arrivals count as on time.
    orders["is_late"] = (actual.dt.normalize() > estimated.dt.normalize()).astype("boolean").where(valid)
    orders["days_late"] = (actual.dt.normalize() - estimated.dt.normalize()).dt.days.where(valid)
    orders["purchase_month"] = purchased.dt.to_period("M")
    return orders


def prepare_data(raw):
    """Build an order fact table and a separate item fact table with safe joins."""
    for table, key in [("orders", ["order_id"]), ("customers", ["customer_id"]),
                       ("products", ["product_id"]), ("sellers", ["seller_id"]),
                       ("translation", ["product_category_name"]),
                       ("items", ["order_id", "order_item_id"]),
                       ("payments", ["order_id", "payment_sequential"])]:
        check_unique(raw[table], key, table)

    # Collapse each one-to-many relationship BEFORE joining it to the order spine.
    item_totals = raw["items"].groupby("order_id", as_index=False).agg(
        product_sales=("price", "sum"), freight_value=("freight_value", "sum"),
        item_count=("order_item_id", "size"), seller_count=("seller_id", "nunique"))
    payment_totals = raw["payments"].groupby("order_id", as_index=False).agg(
        payment_value=("payment_value", "sum"), payment_records=("payment_sequential", "size"))

    orders = (raw["orders"]
              .merge(raw["customers"], on="customer_id", how="left", validate="one_to_one")
              .merge(item_totals, on="order_id", how="left", validate="one_to_one")
              .merge(payment_totals, on="order_id", how="left", validate="one_to_one")
              .merge(select_reviews(raw["reviews"]), on="order_id", how="left", validate="one_to_one"))
    orders = add_delivery_features(orders)
    orders["payment_item_difference"] = orders["payment_value"] - orders["product_sales"] - orders["freight_value"]
    # Missing amounts stay missing. A missing item/payment is not evidence of zero.
    products = raw["products"].merge(raw["translation"], on="product_category_name",
                                      how="left", validate="many_to_one")
    products["category"] = products["product_category_name_english"].fillna(
        "untranslated: " + products["product_category_name"].fillna("unknown"))
    products.loc[products["product_category_name"].isna(), "category"] = "unknown"
    items = (raw["items"]
             .merge(products[["product_id", "category"]], on="product_id", how="left", validate="many_to_one")
             .merge(raw["sellers"], on="seller_id", how="left", validate="many_to_one")
             .merge(orders[["order_id", "order_status", "purchase_month", "customer_state",
                            "delivery_eligible", "is_late"]],
                    on="order_id", how="left", validate="many_to_one"))
    items["category"] = items["category"].fillna("unknown")
    delivered = orders.loc[orders["order_status"].eq("delivered")].copy()
    delivered_items = items.loc[items["order_status"].eq("delivered")].copy()
    return orders, items, delivered, delivered_items


def quality_diagnostics(raw, orders, items):
    """Count issues explicitly. Expected missingness is not automatically an error."""
    checks = {}
    relationships = [
        ("orders", "customer_id", "customers", "customer_id"),
        ("items", "order_id", "orders", "order_id"),
        ("payments", "order_id", "orders", "order_id"),
        ("reviews", "order_id", "orders", "order_id"),
        ("items", "product_id", "products", "product_id"),
        ("items", "seller_id", "sellers", "seller_id"),
    ]
    for child, col, parent, key in relationships:
        checks[f"{child}_{col}_unmatched_rows"] = int((~raw[child][col].isin(raw[parent][key])).sum())
    d = orders.loc[orders["order_status"].eq("delivered")]
    checks.update({
        "order_rows_after_joins": len(orders),
        "item_rows_after_joins": len(items),
        "orders_with_multiple_review_rows": int(raw["reviews"].groupby("order_id").size().gt(1).sum()),
        "review_rows_not_selected": len(raw["reviews"]) - len(select_reviews(raw["reviews"])),
        "delivered_without_valid_delivery_dates": int((~d["delivery_eligible"]).sum()),
        "delivered_without_items": int(d["product_sales"].isna().sum()),
        "delivered_without_payments": int(d["payment_value"].isna().sum()),
        "delivered_without_review": int(d["review_score"].isna().sum()),
        "delivered_payment_difference_over_005_brl": int(d["payment_item_difference"].abs().gt(.05).sum()),
        "items_with_unknown_category": int(items["category"].eq("unknown").sum()),
        "items_with_untranslated_category": int(items["category"].str.startswith("untranslated:").sum()),
        "invalid_review_scores": int((~raw["reviews"]["review_score"].between(1, 5)).sum()),
        "negative_item_prices": int(raw["items"]["price"].lt(0).sum()),
        "negative_freight_values": int(raw["items"]["freight_value"].lt(0).sum()),
        "negative_payment_values": int(raw["payments"]["payment_value"].lt(0).sum()),
    })
    return pd.DataFrame([{"check": k, "count": v} for k, v in checks.items()])


def monthly_sales(delivered):
    result = delivered.groupby("purchase_month").agg(
        orders=("order_id", "size"), product_sales=("product_sales", "sum"),
        freight_value=("freight_value", "sum"), payment_value=("payment_value", "sum"))
    months = pd.period_range(result.index.min(), result.index.max(), freq="M")
    result = result.reindex(months, fill_value=0).rename_axis("purchase_month")
    result["product_aov"] = result["product_sales"] / result["orders"].replace(0, np.nan)
    result["sales_mom_pct"] = result["product_sales"].pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan) * 100
    return result


def category_sales(delivered_items):
    result = delivered_items.groupby("category").agg(
        product_sales=("price", "sum"), freight_value=("freight_value", "sum"),
        item_rows=("order_item_id", "size"), distinct_orders=("order_id", "nunique"))
    result["sales_share_pct"] = result["product_sales"] / result["product_sales"].sum() * 100
    return result.sort_values("product_sales", ascending=False)


def state_performance(delivered):
    result = delivered.groupby("customer_state").agg(
        orders=("order_id", "size"), product_sales=("product_sales", "sum"),
        eligible_deliveries=("delivery_eligible", "sum"), late_orders=("is_late", "sum"),
        median_delivery_days=("delivery_days", "median"))
    result["late_rate_pct"] = 100 * result["late_orders"] / result["eligible_deliveries"].replace(0, np.nan)
    return result.sort_values("late_orders", ascending=False)


def wilson_interval(successes, total, confidence=.95):
    """Wilson score interval for a proportion; undefined for an empty group."""
    if total == 0:
        return np.nan, np.nan
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return max(0., centre - margin), min(1., centre + margin)


def delivery_reviews(delivered):
    eligible = delivered.loc[delivered["delivery_eligible"] & delivered["review_score"].between(1, 5)].copy()
    eligible["delivery_group"] = np.where(eligible["is_late"], "Late", "On time")
    eligible["low_score"] = eligible["review_score"].le(2)
    result = eligible.groupby("delivery_group").agg(
        reviewed_orders=("order_id", "size"), average_score=("review_score", "mean"),
        low_score_orders=("low_score", "sum")).reindex(["On time", "Late"])
    result["low_score_rate_pct"] = 100 * result["low_score_orders"] / result["reviewed_orders"]
    intervals = [wilson_interval(int(row.low_score_orders), int(row.reviewed_orders))
                 for row in result.itertuples()]
    result["ci_low_pct"] = [100 * x[0] for x in intervals]
    result["ci_high_pct"] = [100 * x[1] for x in intervals]
    return result


def customer_summary(delivered):
    return delivered.groupby("customer_unique_id").agg(
        delivered_orders=("order_id", "nunique"), product_sales=("product_sales", "sum"),
        first_purchase=("order_purchase_timestamp", "min"),
        last_purchase=("order_purchase_timestamp", "max"))


def cohort_retention(delivered, cutoff="2018-07-31", first_cohort="2017-01", max_age=6):
    """Observed repeat purchasing, not subscription retention or lifetime churn.

    First purchase means first DELIVERED order observed in this extract.
    Blank cells are unobserved months, while 0 means observed with no returners.
    """
    cutoff_month = pd.Period(cutoff, freq="M")
    end_exclusive = pd.Timestamp(cutoff) + pd.Timedelta(days=1)
    activity = delivered.loc[delivered["order_purchase_timestamp"] < end_exclusive,
                             ["customer_unique_id", "purchase_month"]].drop_duplicates()
    first = activity.groupby("customer_unique_id")["purchase_month"].min().rename("cohort")
    activity = activity.merge(first, on="customer_unique_id", validate="many_to_one")
    activity = activity.loc[activity["cohort"] >= pd.Period(first_cohort, freq="M")].copy()
    activity["month_age"] = activity["purchase_month"].astype("int64") - activity["cohort"].astype("int64")
    cohort_sizes = first.loc[first.ge(pd.Period(first_cohort, freq="M"))].value_counts().sort_index()
    cohort_sizes.index.name = "cohort"
    cohort_sizes.name = "new_customers"
    counts = activity.groupby(["cohort", "month_age"])["customer_unique_id"].nunique().unstack()
    counts = counts.reindex(index=cohort_sizes.index, columns=range(max_age + 1)).fillna(0)
    for cohort in counts.index:
        observed_age = cutoff_month.ordinal - cohort.ordinal
        counts.loc[cohort, counts.columns > observed_age] = np.nan
    rates = counts.div(cohort_sizes, axis=0) * 100
    return counts, rates, cohort_sizes


def seller_performance(delivered_items):
    sales = delivered_items.groupby("seller_id").agg(product_sales=("price", "sum"))
    # One seller-order row: an order with three items from one seller counts once.
    seller_orders = delivered_items.drop_duplicates(["seller_id", "order_id"])
    service = seller_orders.groupby("seller_id").agg(
        distinct_orders=("order_id", "size"), eligible_orders=("delivery_eligible", "sum"),
        late_orders=("is_late", "sum"))
    result = sales.join(service)
    result["late_rate_pct"] = result["late_orders"] / result["eligible_orders"].replace(0, np.nan) * 100
    return result.sort_values("product_sales", ascending=False)


def headline_metrics(raw, orders, delivered, customers, reviews, categories):
    eligible = delivered.loc[delivered["delivery_eligible"]]
    return {
        "raw_orders": len(orders), "delivered_orders": len(delivered),
        "delivered_share_pct": len(delivered) / len(orders) * 100,
        "product_sales_brl": float(delivered["product_sales"].sum()),
        "freight_brl": float(delivered["freight_value"].sum()),
        "payments_brl": float(delivered["payment_value"].sum()),
        "product_aov_brl": float(delivered["product_sales"].sum() / len(delivered)),
        "eligible_deliveries": len(eligible), "late_orders": int(eligible["is_late"].sum()),
        "late_rate_pct": float(eligible["is_late"].mean() * 100),
        "median_delivery_days": float(eligible["delivery_days"].median()),
        "unique_delivered_customers": len(customers),
        "repeat_customers": int(customers["delivered_orders"].gt(1).sum()),
        "observed_repeat_customer_pct": float(customers["delivered_orders"].gt(1).mean() * 100),
        "on_time_review_score": float(reviews.loc["On time", "average_score"]),
        "late_review_score": float(reviews.loc["Late", "average_score"]),
        "on_time_low_score_pct": float(reviews.loc["On time", "low_score_rate_pct"]),
        "late_low_score_pct": float(reviews.loc["Late", "low_score_rate_pct"]),
        "top_category": str(categories.index[0]),
        "top_category_sales_brl": float(categories.iloc[0]["product_sales"]),
        "all_purchase_start": str(orders["order_purchase_timestamp"].min()),
        "all_purchase_end": str(orders["order_purchase_timestamp"].max()),
        "delivered_purchase_start": str(delivered["order_purchase_timestamp"].min()),
        "delivered_purchase_end": str(delivered["order_purchase_timestamp"].max()),
    }


def validate_results(raw, orders, items, delivered, categories, monthly, states, review_summary):
    """Reconcile independent sources so an accidental many-to-many join is caught."""
    checks = []

    def record(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    record("one_order_row_per_source_order", len(orders) == len(raw["orders"]) and orders["order_id"].is_unique)
    record("item_row_count_preserved", len(items) == len(raw["items"]))
    source_items = raw["items"].loc[raw["items"]["order_id"].isin(delivered["order_id"])]
    record("delivered_sales_match_raw_items", np.isclose(delivered["product_sales"].sum(), source_items["price"].sum(), rtol=0, atol=.01))
    source_payments = raw["payments"].loc[raw["payments"]["order_id"].isin(delivered["order_id"])]
    record("delivered_payments_match_raw_payments", np.isclose(delivered["payment_value"].sum(), source_payments["payment_value"].sum(), rtol=0, atol=.01))
    for name, total in [("category", categories["product_sales"].sum()),
                        ("month", monthly["product_sales"].sum()),
                        ("state", states["product_sales"].sum())]:
        record(f"{name}_sales_reconcile", np.isclose(total, source_items["price"].sum(), rtol=0, atol=.01))
    record("all_delivered_orders_have_items", delivered["product_sales"].notna().all())
    record("review_groups_match_eligible_reviewed_orders", review_summary["reviewed_orders"].sum() ==
           (delivered["delivery_eligible"] & delivered["review_score"].between(1, 5)).sum())
    record("unknown_deliveries_not_classified_on_time", orders.loc[~orders["delivery_eligible"], "is_late"].isna().all())
    result = pd.DataFrame(checks)
    if not result["passed"].all():
        raise AssertionError(result.to_string(index=False))
    return result


def source_manifest(data_dir):
    """Record exact source bytes for reproducibility; no network access required."""
    rows = []
    for filename in FILES.values():
        path = Path(data_dir) / filename
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        rows.append({"filename": filename, "bytes": path.stat().st_size, "sha256": digest.hexdigest()})
    return pd.DataFrame(rows)
