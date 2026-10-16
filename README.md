# Product Mix Optimization Using Linear Programming

## Task 4 – Data Science Internship

## Project Objective

Demonstrate how integer linear programming can select a profitable manufacturing product mix while respecting finite resources and market demand.

## Business Problem

A manufacturing company produces Products A, B, and C. This educational case uses synthetic data to maximize total profit subject to labor, raw material, machine-hour, demand, non-negativity, and integer constraints.

## Business Scenario

Each product has a different unit profit and consumes labor, material, and machine time. The company must decide how many whole units of each product to produce.

## Mathematical Formulation

### Decision Variables

`A`, `B`, and `C` are non-negative integer production quantities.

### Objective Function

Maximize `40A + 55B + 70C`.

### Constraints

- Labor: `2A + 3B + 4C <= 300`
- Material: `3A + 4B + 5C <= 420`
- Machine: `A + 2B + 3C <= 180`
- Demand: `A <= 100`, `B <= 80`, `C <= 60`

## Technologies

Python, PuLP (CBC solver), pandas, NumPy, Matplotlib, and Jupyter.

## Project Structure

```text
Product_Mix_Optimization_Task_4/
├── notebooks/product_mix_optimization.ipynb
├── src/optimization.py
├── results/optimization_results.csv
├── results/resource_utilization.csv
├── results/optimal_production_mix.png
├── results/resource_utilization.png
├── results/profit_contribution.png
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## How to Run

```powershell
.\.venv\Scripts\python.exe src\optimization.py
```

## Notebook

Execute `notebooks/product_mix_optimization.ipynb` with Jupyter or nbconvert. It uses the same model and data as the Python script.

## Results

The executed CBC model returned **Optimal**:

| Product | Optimal quantity | Profit contribution |
|---|---:|---:|
| Product A | 90 | $3,600 |
| Product B | 0 | $0 |
| Product C | 30 | $2,100 |

**Total production:** 120 units  
**Maximum total profit:** **$5,700**

| Resource | Used | Capacity | Remaining | Utilization |
|---|---:|---:|---:|---:|
| Labor | 300 | 300 | 0 | 100.00% |
| Material | 420 | 420 | 0 | 100.00% |
| Machine | 180 | 180 | 0 | 100.00% |

All three resources are tied for the main bottleneck because each is fully utilized. No demand limit is binding.

## Business Insights

The solution produces 90 units of A and 30 units of C. Product A contributes the most total profit because of its larger quantity, while all three capacity constraints bind. Product B is not selected in the optimum because the solver finds a better feasible allocation of the scarce resources using A and C.

## Limitations

The data is synthetic and educational, not confidential company information. Demand and resource availability are assumed. The model is deterministic and does not explicitly model uncertainty, setup costs, workforce shifts, inventory, lead times, or other real-world constraints.

## Conclusion

PuLP provides an auditable integer linear programming solution: the recommended mix maximizes profit at $5,700 while satisfying every stated constraint.
