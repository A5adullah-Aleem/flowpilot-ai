
import json
from pathlib import Path

import pandas as pd
from langchain_core.tools import tool


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_FILE = PROJECT_ROOT / "data" / "sales.csv"


@tool
def analyze_sales(top_n: int = 5) -> str:
    """
    Analyze sales data and calculate business metrics.

    Calculates revenue, units sold, top products, monthly revenue,
    average monthly growth, order metrics, and profit metrics
    when the required columns are available.

    Args:
        top_n: Number of top products to return.
    """

    if top_n < 1 or top_n > 20:
        return "Error: top_n must be between 1 and 20."

    if not SALES_FILE.exists():
        return "Error: Sales CSV file was not found."

    try:
        df = pd.read_csv(SALES_FILE)

        required_columns = {
            "order_date",
            "product",
            "quantity",
            "unit_price",
            "region",
        }

        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            return f"Error: Missing columns: {sorted(missing_columns)}"

        if df.empty:
            return "Error: Sales dataset is empty."

        # Convert data types
        df["order_date"] = pd.to_datetime(
            df["order_date"], errors="coerce"
        )

        for column in ["quantity", "unit_price"]:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            )

        # Validate optional columns
        has_order_id = "order_id" in df.columns
        has_unit_cost = "unit_cost" in df.columns

        if has_order_id:
            df["order_id"] = df["order_id"].astype("string").str.strip()

        if has_unit_cost:
            df["unit_cost"] = pd.to_numeric(
                df["unit_cost"], errors="coerce"
            )

        # Remove rows with invalid required values
        df = df.dropna(
            subset=[
                "order_date",
                "product",
                "quantity",
                "unit_price",
            ]
        )

        df["product"] = df["product"].astype(str).str.strip()

        df = df[df["product"] != ""]

        if has_order_id:
            df = df.dropna(subset=["order_id"])
            df = df[df["order_id"] != ""]

        if df.empty:
            return "Error: No valid sales records found."

        if (
            (df["quantity"] < 0).any()
            or (df["unit_price"] < 0).any()
        ):
            return "Error: Negative quantities or prices are not supported."

        if has_unit_cost:
            if df["unit_cost"].isna().any():
                return "Error: unit_cost contains missing or invalid values."

            if (df["unit_cost"] < 0).any():
                return "Error: Negative unit costs are not supported."
            
            
            

        # Calculate revenue
        df["revenue"] = df["quantity"] * df["unit_price"]

        total_revenue = df["revenue"].sum()
        total_units = df["quantity"].sum()

        # Order metrics
        if has_order_id:
            total_orders = int(df["order_id"].nunique())
            average_order_value = (
                total_revenue / total_orders
                if total_orders > 0
                else None
            )
        else:
            total_orders = None
            average_order_value = None

        # Profit metrics
        if has_unit_cost:
            df["gross_profit"] = (
                df["quantity"] *
                (df["unit_price"] - df["unit_cost"])
            )

            total_gross_profit = df["gross_profit"].sum()

            total_cost = (
                df["quantity"] * df["unit_cost"]
            ).sum()

            gross_profit_margin = (
                (total_gross_profit / total_revenue) * 100
                if total_revenue > 0
                else None
            )
        else:
            total_gross_profit = None
            gross_profit_margin = None
            total_cost = None

        # Top products by revenue
        top_products = (
            df.groupby("product")
            .agg(
                units_sold=("quantity", "sum"),
                revenue=("revenue", "sum"),
            )
            .sort_values("revenue", ascending=False)
            .head(top_n)
            .reset_index()
        )

        # Monthly revenue and growth
        df["month"] = df["order_date"].dt.to_period("M")

        monthly = (
            df.groupby("month")["revenue"]
            .sum()
            .sort_index()
            .reset_index()
        )

        monthly["growth_percentage"] = (
            monthly["revenue"].pct_change() * 100
        )

        # Average of available month-over-month growth rates
        valid_growth = monthly["growth_percentage"].dropna()

        average_mom_growth = (
            float(valid_growth.mean())
            if not valid_growth.empty
            else None
        )

        monthly_revenue = []

        for _, row in monthly.iterrows():
            growth = row["growth_percentage"]

            monthly_revenue.append({
                "month": str(row["month"]),
                "revenue": round(float(row["revenue"]), 2),
                "growth_percentage": (
                    round(float(growth), 2)
                    if pd.notna(growth)
                    else None
                ),
            })
            
                # Product-level profitability
        product_profitability = []

        if has_unit_cost:
            df["cost"] = df["quantity"] * df["unit_cost"]

            product_data = (
                df.groupby("product")
                .agg(
                    units_sold=("quantity", "sum"),
                    revenue=("revenue", "sum"),
                    total_cost=("cost", "sum"),
                )
                .reset_index()
            )

            product_data["gross_profit"] = (
                product_data["revenue"] - product_data["total_cost"]
            )

            product_data["profit_margin_percentage"] = (
                product_data["gross_profit"]
                / product_data["revenue"].replace(0, float("nan"))
                * 100
            )

            product_profitability = (
                product_data.fillna(0)
                .round(2)
                .to_dict(orient="records")
            )



        top_margin_products = product_data.nlargest(
            3, "profit_margin_percentage"
            )

        top_margin_summary = {
            "products": top_margin_products["product"].tolist(),
            "combined_revenue": round(
            float(top_margin_products["revenue"].sum()), 2
            ),
            "combined_gross_profit": round(
                float(top_margin_products["gross_profit"].sum()), 2
            ),
            "revenue_share_percentage": round(
            float(
                top_margin_products["revenue"].sum()
                / total_revenue * 100
            ), 2
        ) 
            if total_revenue > 0 else None,
                "profit_share_percentage": round(
                float(
                top_margin_products["gross_profit"].sum()
                    / total_gross_profit * 100
                ), 2
            ) 
            if total_gross_profit > 0 else None,
        }


        # Final structured result
        result = {
            "summary": {
                "total_revenue": round(float(total_revenue), 2),
                "total_units_sold": round(float(total_units), 2),
                "total_sales_records": int(len(df)),
                "total_orders": total_orders,
                "average_order_value": (
                    round(float(average_order_value), 2)
                    if average_order_value is not None
                    else None
                ),
                "total_cost": (
                    round(float(total_cost), 2)
                    if total_cost is not None
                    else None
                ),
                "total_gross_profit": (
                    round(float(total_gross_profit), 2)
                    if total_gross_profit is not None
                    else None
                ),
                "gross_profit_margin_percentage": (
                    round(float(gross_profit_margin), 2)
                    if gross_profit_margin is not None
                    else None
                ),
                "average_mom_growth_percentage": (
                    round(average_mom_growth, 2)
                    if average_mom_growth is not None
                    else None
                ),
            },
            "top_products": [
                {
                    "product": row["product"],
                    "units_sold": float(row["units_sold"]),
                    "revenue": round(float(row["revenue"]), 2),
                }
                for _, row in top_products.iterrows()
            ],
            
            "product_profitability": product_profitability,
            "top_margin_products_summary": top_margin_summary,
            "monthly_revenue": monthly_revenue,
            "available_metrics": {
                "order_metrics": has_order_id,
                "profit_metrics": has_unit_cost,
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error analyzing sales data: {str(e)}"
