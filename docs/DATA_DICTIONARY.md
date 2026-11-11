# Data dictionary

Observed row counts and missing values are computed from the supplied CSVs.
Field names preserve source spelling. Primary metric definitions and derived
features are documented in [DATA_NOTES.md](DATA_NOTES.md).

Source: [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## olist_orders_dataset.csv

**Rows:** 99,441 · **Columns:** 8 · **Key:** Unique order_id

| Field | Missing rows | Meaning |
|---|---:|---|
| `order_id` | 0 | Order identifier; foreign key to orders in the child tables. |
| `customer_id` | 0 | Order-specific customer record identifier; not a repeat-buyer identity. |
| `order_status` | 0 | Recorded order status; commercial scope selects delivered. |
| `order_purchase_timestamp` | 0 | Purchase timestamp, analysed as supplied. |
| `order_approved_at` | 160 | Order approval timestamp; can be missing. |
| `order_delivered_carrier_date` | 1,783 | Recorded carrier handoff timestamp; can be missing. |
| `order_delivered_customer_date` | 2,965 | Recorded customer delivery timestamp; can be missing. |
| `order_estimated_delivery_date` | 0 | Estimated delivery date, generally stored at midnight. |

## olist_customers_dataset.csv

**Rows:** 99,441 · **Columns:** 5 · **Key:** Unique customer_id

| Field | Missing rows | Meaning |
|---|---:|---|
| `customer_id` | 0 | Order-specific customer record identifier; not a repeat-buyer identity. |
| `customer_unique_id` | 0 | Stable anonymised customer identifier for observed repeat purchases. |
| `customer_zip_code_prefix` | 0 | Five-digit ZIP prefix; loaded as string to preserve leading zeros. |
| `customer_city` | 0 | Customer city label as supplied; not normalised for this state-level analysis. |
| `customer_state` | 0 | Customer state abbreviation; destination for state-level analysis. |

## olist_order_items_dataset.csv

**Rows:** 112,650 · **Columns:** 7 · **Key:** Unique (order_id, order_item_id)

| Field | Missing rows | Meaning |
|---|---:|---|
| `order_id` | 0 | Order identifier; foreign key to orders in the child tables. |
| `order_item_id` | 0 | Item sequence within the order, not a globally unique item identifier. |
| `product_id` | 0 | Product identifier; foreign key to products. |
| `seller_id` | 0 | Seller identifier; foreign key to sellers. |
| `shipping_limit_date` | 0 | Recorded seller shipping deadline timestamp. |
| `price` | 0 | Price of this item position, in BRL; no separate quantity field is supplied. |
| `freight_value` | 0 | Freight charge assigned to this item position, in BRL. |

## olist_order_payments_dataset.csv

**Rows:** 103,886 · **Columns:** 5 · **Key:** Unique (order_id, payment_sequential)

| Field | Missing rows | Meaning |
|---|---:|---|
| `order_id` | 0 | Order identifier; foreign key to orders in the child tables. |
| `payment_sequential` | 0 | Payment sequence within the order; an order can have split payments. |
| `payment_type` | 0 | Recorded payment method. |
| `payment_installments` | 0 | Recorded installment count; not used to multiply payment value. |
| `payment_value` | 0 | Value of this payment record in BRL; sum split payments per order. |

## olist_order_reviews_dataset.csv

**Rows:** 99,224 · **Columns:** 7 · **Key:** No single-column key assumed; select one row per order for analysis

| Field | Missing rows | Meaning |
|---|---:|---|
| `review_id` | 0 | Source review identifier; not assumed unique in this extract. |
| `order_id` | 0 | Order identifier; foreign key to orders in the child tables. |
| `review_score` | 0 | Integer customer review score, 1–5; low score is defined as 1 or 2. |
| `review_comment_title` | 87,656 | Optional review title; not used in calculations. |
| `review_comment_message` | 58,247 | Optional anonymised review text; not used in calculations. |
| `review_creation_date` | 0 | Recorded review survey creation date; tie-breaker for review selection. |
| `review_answer_timestamp` | 0 | Recorded review answer timestamp; latest response selects the main score. |

## olist_products_dataset.csv

**Rows:** 32,951 · **Columns:** 9 · **Key:** Unique product_id

| Field | Missing rows | Meaning |
|---|---:|---|
| `product_id` | 0 | Product identifier; foreign key to products. |
| `product_category_name` | 610 | Original Portuguese category label; can be missing. |
| `product_name_lenght` | 610 | Recorded product-name length; original source spelling retained. |
| `product_description_lenght` | 610 | Recorded description length; original source spelling retained. |
| `product_photos_qty` | 610 | Recorded product-photo count. |
| `product_weight_g` | 2 | Product weight in grams. |
| `product_length_cm` | 2 | Product length in centimetres. |
| `product_height_cm` | 2 | Product height in centimetres. |
| `product_width_cm` | 2 | Product width in centimetres. |

## olist_sellers_dataset.csv

**Rows:** 3,095 · **Columns:** 4 · **Key:** Unique seller_id

| Field | Missing rows | Meaning |
|---|---:|---|
| `seller_id` | 0 | Seller identifier; foreign key to sellers. |
| `seller_zip_code_prefix` | 0 | Seller five-digit ZIP prefix; loaded as string. |
| `seller_city` | 0 | Seller city label as supplied. |
| `seller_state` | 0 | Seller state abbreviation. |

## product_category_name_translation.csv

**Rows:** 71 · **Columns:** 2 · **Key:** Unique product_category_name

| Field | Missing rows | Meaning |
|---|---:|---|
| `product_category_name` | 0 | Original Portuguese category label; can be missing. |
| `product_category_name_english` | 0 | English category translation supplied with the source dataset. |

## olist_geolocation_dataset.csv

**Rows:** 1,000,163 · **Columns:** 5 · **Key:** No unique ZIP-prefix key

| Field | Missing rows | Meaning |
|---|---:|---|
| `geolocation_zip_code_prefix` | 0 | Five-digit ZIP prefix; many source rows per prefix. |
| `geolocation_lat` | 0 | Latitude observation; no coordinate cleaning or mapping performed. |
| `geolocation_lng` | 0 | Longitude observation; no coordinate cleaning or mapping performed. |
| `geolocation_city` | 0 | City label of the coordinate observation. |
| `geolocation_state` | 0 | State abbreviation of the coordinate observation. |
