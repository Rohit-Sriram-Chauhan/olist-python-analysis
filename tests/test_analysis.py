"""Small synthetic examples that catch mistakes large totals can hide.

Run: python -m unittest discover -s tests -v
"""

import unittest
import numpy as np
import pandas as pd
from src.analysis import prepare_data, add_delivery_features, select_reviews, cohort_retention, wilson_interval


def small_dataset():
    """Two orders, with several items/payments/reviews on the first order."""
    orders = pd.DataFrame({
        "order_id": ["o1", "o2"], "customer_id": ["c1", "c2"],
        "order_status": ["delivered", "delivered"],
        "order_purchase_timestamp": pd.to_datetime(["2018-01-01 10:00", "2018-01-02 10:00"]),
        "order_delivered_customer_date": pd.to_datetime(["2018-01-05 19:00", None]),
        "order_estimated_delivery_date": pd.to_datetime(["2018-01-05", "2018-01-08"]),
    })
    return {
        "orders": orders,
        "customers": pd.DataFrame({"customer_id": ["c1", "c2"], "customer_unique_id": ["u1", "u1"],
                                   "customer_state": ["SP", "SP"]}),
        "items": pd.DataFrame({"order_id": ["o1", "o1", "o2"], "order_item_id": [1, 2, 1],
                               "product_id": ["p1", "p2", "p1"], "seller_id": ["s1", "s1", "s1"],
                               "price": [10., 20., 5.], "freight_value": [2., 3., 1.]}),
        "payments": pd.DataFrame({"order_id": ["o1", "o1", "o2"], "payment_sequential": [1, 2, 1],
                                  "payment_value": [15., 20., 6.]}),
        "reviews": pd.DataFrame({"order_id": ["o1", "o1", "o2"], "review_id": ["r1", "r2", "r3"],
                                 "review_score": [1, 5, 2],
                                 "review_creation_date": pd.to_datetime(["2018-01-06", "2018-01-08", "2018-01-09"]),
                                 "review_answer_timestamp": pd.to_datetime(["2018-01-07", "2018-01-09", "2018-01-10"])}),
        "products": pd.DataFrame({"product_id": ["p1", "p2"], "product_category_name": ["a", "b"]}),
        "translation": pd.DataFrame({"product_category_name": ["a", "b"], "product_category_name_english": ["A", "B"]}),
        "sellers": pd.DataFrame({"seller_id": ["s1"], "seller_state": ["SP"]}),
    }


class AnalysisTests(unittest.TestCase):
    def test_multiple_items_payments_and_reviews_do_not_multiply_money(self):
        orders, items, delivered, _ = prepare_data(small_dataset())
        self.assertEqual(len(orders), 2)
        self.assertEqual(len(items), 3)
        self.assertEqual(orders.loc[orders.order_id.eq("o1"), "product_sales"].item(), 30)
        self.assertEqual(orders.loc[orders.order_id.eq("o1"), "payment_value"].item(), 35)
        self.assertEqual(delivered.product_sales.sum(), 35)

    def test_arrival_on_promised_date_is_on_time_even_after_midnight(self):
        orders = add_delivery_features(small_dataset()["orders"])
        self.assertFalse(orders.loc[0, "is_late"])

    def test_missing_delivery_date_is_not_assumed_on_time(self):
        orders = add_delivery_features(small_dataset()["orders"])
        self.assertFalse(orders.loc[1, "delivery_eligible"])
        self.assertTrue(pd.isna(orders.loc[1, "is_late"]))
        self.assertTrue(pd.isna(orders.loc[1, "delivery_days"]))

    def test_latest_review_policy_can_be_compared_with_earliest(self):
        reviews = small_dataset()["reviews"]
        self.assertEqual(select_reviews(reviews).set_index("order_id").loc["o1", "review_score"], 5)
        self.assertEqual(select_reviews(reviews, keep="first").set_index("order_id").loc["o1", "review_score"], 1)

    def test_duplicate_dimension_key_stops_instead_of_silently_dropping_rows(self):
        raw = small_dataset()
        raw["products"] = pd.concat([raw["products"], raw["products"].iloc[[0]]])
        with self.assertRaisesRegex(ValueError, "products"):
            prepare_data(raw)

    def test_missing_payment_is_preserved_as_unknown(self):
        raw = small_dataset()
        raw["payments"] = raw["payments"].loc[raw["payments"].order_id.ne("o2")]
        orders, _, _, _ = prepare_data(raw)
        self.assertTrue(pd.isna(orders.set_index("order_id").loc["o2", "payment_value"]))

    def test_cohorts_distinguish_zero_from_not_yet_observable(self):
        d = pd.DataFrame({"customer_unique_id": ["u1", "u1", "u2", "u3"],
                          "order_purchase_timestamp": pd.to_datetime(["2018-01-02", "2018-03-02", "2018-02-02", "2018-03-03"])})
        d["purchase_month"] = d.order_purchase_timestamp.dt.to_period("M")
        counts, rates, sizes = cohort_retention(d, cutoff="2018-03-31", first_cohort="2018-01", max_age=3)
        jan, feb, mar = [pd.Period(p, "M") for p in ["2018-01", "2018-02", "2018-03"]]
        self.assertEqual(rates.loc[jan, 1], 0)
        self.assertEqual(rates.loc[jan, 2], 100)
        self.assertEqual(rates.loc[feb, 1], 0)
        self.assertTrue(pd.isna(rates.loc[mar, 1]))
        self.assertTrue((rates[0] == 100).all())
        self.assertEqual(sizes.sum(), 3)

    def test_wilson_intervals_handle_empty_and_boundary_groups(self):
        self.assertTrue(np.isnan(wilson_interval(0, 0)[0]))
        lo, hi = wilson_interval(0, 10)
        self.assertAlmostEqual(lo, 0)
        self.assertGreater(hi, 0)
        lo, hi = wilson_interval(10, 10)
        self.assertLess(lo, 1)
        self.assertAlmostEqual(hi, 1)


if __name__ == "__main__":
    unittest.main()
