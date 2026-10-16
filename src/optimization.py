"""Product mix optimization using integer linear programming."""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import pulp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

DATA: dict[str, Any] = {
    "products": ["A", "B", "C"],
    "profit": {"A": 40, "B": 55, "C": 70},
    "labor": {"A": 2, "B": 3, "C": 4},
    "material": {"A": 3, "B": 4, "C": 5},
    "machine": {"A": 1, "B": 2, "C": 3},
    "demand": {"A": 100, "B": 80, "C": 60},
    "capacity": {"Labor": 300, "Material": 420, "Machine": 180},
}


def build_problem(data: dict[str, Any] = DATA) -> tuple[pulp.LpProblem, dict[str, pulp.LpVariable]]:
    """Build and return the PuLP model and integer production variables."""
    problem = pulp.LpProblem("Product_Mix_Optimization", pulp.LpMaximize)
    quantities = pulp.LpVariable.dicts(
        "Production",
        data["products"],
        lowBound=0,
        cat="Integer",
    )
    problem += pulp.lpSum(data["profit"][p] * quantities[p] for p in data["products"])
    problem += pulp.lpSum(data["labor"][p] * quantities[p] for p in data["products"]) <= data["capacity"]["Labor"], "Labor_Capacity"
    problem += pulp.lpSum(data["material"][p] * quantities[p] for p in data["products"]) <= data["capacity"]["Material"], "Material_Capacity"
    problem += pulp.lpSum(data["machine"][p] * quantities[p] for p in data["products"]) <= data["capacity"]["Machine"], "Machine_Capacity"
    for product in data["products"]:
        problem += quantities[product] <= data["demand"][product], f"{product}_Demand"
    return problem, quantities


def solve_problem(
    data: dict[str, Any] = DATA,
) -> tuple[pulp.LpProblem, dict[str, pulp.LpVariable]]:
    """Solve the model with CBC and require an optimal solution."""
    problem, quantities = build_problem(data)
    problem.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[problem.status]
    if status != "Optimal":
        raise RuntimeError(f"Optimization failed with solver status: {status}")
    return problem, quantities


def calculate_resource_usage(
    quantities: dict[str, pulp.LpVariable], data: dict[str, Any] = DATA
) -> pd.DataFrame:
    """Calculate used, remaining, and percentage utilization for each resource."""
    rows = []
    for resource, requirements in (
        ("Labor", data["labor"]),
        ("Material", data["material"]),
        ("Machine", data["machine"]),
    ):
        used = sum(requirements[p] * quantities[p].value() for p in data["products"])
        capacity = data["capacity"][resource]
        rows.append(
            {
                "Resource": resource,
                "Used": used,
                "Capacity": capacity,
                "Remaining": capacity - used,
                "Utilization_%": used / capacity * 100,
            }
        )
    return pd.DataFrame(rows)


def create_results_tables(
    quantities: dict[str, pulp.LpVariable], data: dict[str, Any] = DATA
) -> tuple[pd.DataFrame, pd.DataFrame, int, float]:
    """Create product and resource result tables from solver values."""
    product_rows = []
    for product in data["products"]:
        quantity = int(round(quantities[product].value()))
        product_rows.append(
            {
                "Product": f"Product {product}",
                "Optimal_Quantity": quantity,
                "Profit_Per_Unit": data["profit"][product],
                "Total_Profit": quantity * data["profit"][product],
            }
        )
    product_results = pd.DataFrame(product_rows)
    resource_results = calculate_resource_usage(quantities, data)
    total_production = int(product_results["Optimal_Quantity"].sum())
    total_profit = float(product_results["Total_Profit"].sum())
    return product_results, resource_results, total_production, total_profit


def save_results(
    product_results: pd.DataFrame,
    resource_results: pd.DataFrame,
    directory: Path = RESULTS_DIR,
) -> None:
    """Save required CSV files and three readable Matplotlib charts."""
    directory.mkdir(parents=True, exist_ok=True)
    product_results.to_csv(directory / "optimization_results.csv", index=False)
    resource_results.to_csv(directory / "resource_utilization.csv", index=False)

    def add_values(axis: Any, bars: Any) -> None:
        axis.bar_label(bars, fmt="%.0f", padding=3)

    fig, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(product_results["Product"], product_results["Optimal_Quantity"], color="#2563eb")
    axis.set(title="Optimal Production Mix", xlabel="Product", ylabel="Optimal Quantity (units)")
    add_values(axis, bars)
    fig.tight_layout()
    fig.savefig(directory / "optimal_production_mix.png", dpi=180)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(resource_results["Resource"], resource_results["Utilization_%"], color="#16a34a")
    axis.set(title="Resource Utilization", xlabel="Resource", ylabel="Utilization (%)")
    axis.set_ylim(0, max(100, resource_results["Utilization_%"].max() * 1.15))
    add_values(axis, bars)
    fig.tight_layout()
    fig.savefig(directory / "resource_utilization.png", dpi=180)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(product_results["Product"], product_results["Total_Profit"], color="#f59e0b")
    axis.set(title="Profit Contribution", xlabel="Product", ylabel="Total Profit ($)")
    add_values(axis, bars)
    fig.tight_layout()
    fig.savefig(directory / "profit_contribution.png", dpi=180)
    plt.close(fig)


def print_business_insights(
    product_results: pd.DataFrame, resource_results: pd.DataFrame, data: dict[str, Any] = DATA
) -> None:
    """Print insights derived from the calculated solution."""
    largest = product_results.loc[product_results["Optimal_Quantity"].idxmax()]
    top_profit = product_results.loc[product_results["Total_Profit"].idxmax()]
    bottlenecks = resource_results[resource_results["Remaining"] == resource_results["Remaining"].min()]["Resource"].tolist()
    unused = resource_results[resource_results["Remaining"] > 0]["Resource"].tolist()
    binding_demand = [
        row["Product"]
        for _, row in product_results.iterrows()
        if row["Optimal_Quantity"] == data["demand"][row["Product"][-1]]
    ]
    print(f"Largest production quantity: {largest['Product']} ({int(largest['Optimal_Quantity'])} units)")
    print(f"Largest profit contribution: {top_profit['Product']} (${top_profit['Total_Profit']:,.0f})")
    print(f"Main bottleneck resource(s): {', '.join(bottlenecks)}")
    print(f"Resources with unused capacity: {', '.join(unused) if unused else 'None'}")
    print(f"Binding demand limit(s): {', '.join(binding_demand) if binding_demand else 'None'}")
    print("Resource allocation insight: the optimal mix prioritizes products while respecting all capacity and demand limits.")


def main() -> None:
    problem, quantities = solve_problem()
    product_results, resource_results, total_production, total_profit = create_results_tables(quantities)
    save_results(product_results, resource_results)
    print(f"Solver Status: {pulp.LpStatus[problem.status]}")
    print(f"Optimal quantities: {dict(zip(product_results['Product'], product_results['Optimal_Quantity']))}")
    print(f"Total production: {total_production}")
    print(f"Maximum profit: ${total_profit:,.0f}")
    print(resource_results.to_string(index=False))
    print_business_insights(product_results, resource_results)


if __name__ == "__main__":
    main()
