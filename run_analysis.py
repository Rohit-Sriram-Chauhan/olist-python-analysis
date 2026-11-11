"""Run from the project folder: python run_analysis.py

The notebook calls the same functions, so calculations have one source of truth.
"""

import argparse
import json
import math
from pathlib import Path

import pandas as pd

from src.analysis import (
    load_data, profile_data, prepare_data, quality_diagnostics, monthly_sales,
    category_sales, state_performance, delivery_reviews, customer_summary,
    cohort_retention, seller_performance, headline_metrics, validate_results,
    source_manifest, select_reviews,
)
from src.charts import create_charts
from src.reporting import create_report


def export_results(tables, metrics, root):
    destination = Path(root) / "outputs" / "tables"
    destination.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(destination / f"{name}.csv", index=not isinstance(table.index, pd.RangeIndex), float_format="%.6f")
    (destination.parent / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def run_project(data_dir=None, root=None):
    root = Path(root or Path(__file__).resolve().parent)
    data_dir = Path(data_dir or root / "data" / "raw")
    raw = load_data(data_dir)
    inventory, missing = profile_data(raw)
    orders, items, delivered, delivered_items = prepare_data(raw)
    monthly = monthly_sales(delivered)
    categories = category_sales(delivered_items)
    states = state_performance(delivered)
    reviews = delivery_reviews(delivered)
    customers = customer_summary(delivered)
    counts, retention, sizes = cohort_retention(delivered)
    sellers = seller_performance(delivered_items)
    diagnostics = quality_diagnostics(raw, orders, items)
    checks = validate_results(raw, orders, items, delivered, categories, monthly, states, reviews)

    # The alternative review selection is a robustness check, not another headline.
    earliest = delivered.drop(columns="review_score").merge(
        select_reviews(raw["reviews"], keep="first"), on="order_id", how="left", validate="one_to_one")
    sensitivity = pd.concat({"latest_response": reviews, "earliest_response": delivery_reviews(earliest)},
                            names=["review_policy"]).reset_index()
    customer_distribution = (customers["delivered_orders"].value_counts().sort_index()
                             .rename_axis("delivered_orders_per_customer").to_frame("customers"))
    tables = {
        "data_inventory": inventory, "missing_values": missing,
        "quality_diagnostics": diagnostics, "validation_checks": checks,
        "order_status": orders["order_status"].value_counts().rename_axis("order_status").to_frame("orders"),
        "monthly_sales": monthly, "category_sales": categories, "state_performance": states,
        "delivery_reviews": reviews, "review_policy_sensitivity": sensitivity,
        "customer_order_distribution": customer_distribution,
        "cohort_customer_counts": counts, "cohort_retention_pct": retention,
        "cohort_sizes": sizes.to_frame(), "seller_performance": sellers,
        "source_manifest": source_manifest(data_dir),
    }
    metrics = headline_metrics(raw, orders, delivered, customers, reviews, categories)
    metrics["top_20pct_sellers_sales_pct"] = float(
        sellers.head(math.ceil(len(sellers) * .2))["product_sales"].sum()
        / sellers["product_sales"].sum() * 100)
    export_results(tables, metrics, root)
    figures = create_charts(tables, metrics, root / "reports" / "figures")
    create_report(tables, metrics, figures, root / "reports" / "executive_report.html")
    return metrics, tables


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild the Olist portfolio outputs from nine raw CSVs.")
    parser.add_argument("--data-dir", type=Path, help="Optional folder containing the original CSV files")
    args = parser.parse_args()
    metrics, tables = run_project(data_dir=args.data_dir)
    print(f"Delivered orders: {metrics['delivered_orders']:,}")
    print(f"Product sales: R$ {metrics['product_sales_brl']:,.2f}")
    print(f"Late delivery rate: {metrics['late_rate_pct']:.2f}%")
    print(f"Validation: {len(tables['validation_checks'])} checks passed")
    print("Created outputs/tables/, reports/figures/ and reports/executive_report.html")
