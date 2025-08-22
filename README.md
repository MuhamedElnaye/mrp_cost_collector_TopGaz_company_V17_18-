# mrp_cost_collector_TopGaz_company_V17_18-
This file defines a custom Odoo model to manage and calculate the costs of product components for manufacturing (BoM-based).

# 📌 Mrp Cost Collector (Odoo Custom Module)

This module provides a **Cost Collector** for manufacturing products in Odoo.  
It calculates the required components from BoM, checks availability across stock locations, and computes missing quantities and costs.

---

## ⚙️ Models

### 1. `mrp.cost.collector`
Represents a cost collection order.

**Fields:**
- `name`: Order name (default: *Planning collector Costs*).
- `ref`: Auto-generated reference from `ir.sequence`.
- `date_time`: Creation timestamp.
- `finished_product_ids`: Finished products to manufacture.
- `global_qty`: Quantities for products (entered as string, e.g., `3-2-1`).
- `location_ids`: Stock locations to check availability.
- `component_line_ids`: Linked required components.
- `total_cost_all`: Total cost of missing components.
- `total_cost_all_with_currency`: Total cost formatted with currency (EGP).

**Methods:**
- `create()`: Auto-fill date and reference sequence.
- `_check_quantities_match()`: Validates quantities match product count.
- `_onchange_products_quantities()`: Auto-calculate components from BoM.
- `compute_components()`: Manual trigger to validate & recalculate.
- `_compute_total_cost_all()`: Compute overall missing cost.
- `open_export_wizard()`: Opens wizard to export components.

---

### 2. `mrp.cost.collector.line`
Represents each required component for the order.

**Fields:**
- `order_id`: Parent `mrp.cost.collector`.
- `product_id`: Component product.
- `required_qty`: Required quantity.
- `available_qty`: Available stock quantity.
- `missing_qty`: Shortage (required - available).
- `purchase_cost`: Unit cost (from product standard price).
- `total_cost`: Total cost for missing components.
- `purchase_cost_with_currency`: Unit cost with currency (EGP).
- `total_cost_with_currency`: Total cost with currency (EGP).

**Methods:**
- `_compute_purchase_cost()`: Get unit cost from product.
- `_compute_total_cost()`: Calculate missing cost.

---

## 🔑 Features
- Auto-computes required & missing components using BoM.
- Strict validation for matching product/quantity count.
- Cost breakdown in **local currency (EGP)**.
- Multi-location stock availability support.
- Export results with an export wizard.

---

## 📂 Usage
1. Create a new **Mrp Cost Collector**.
2. Select finished products and enter quantities (e.g., `2-5-3`).
3. Choose one or more stock locations.
4. Click **Compute Components** → system will calculate required, available, and missing components.
5. View cost details and totals.
6. Use **Export Components** to export the results.

---

## 🏗️ Technical Notes
- Relies on Odoo’s **BoM (`mrp.bom`)** and **stock.quant** for calculations.
- Uses constraints to enforce data correctness.
- Supports `mail.thread` and `mail.activity.mixin` for chatter logging.

---
