# Supermarket Sales and Pricing Strategy Analysis

## Overview
Analysis of 1000 supermarket transactions across 6 product 
categories and 3 branches to find the optimal pricing strategy.

## Tools Used
- Python (Pandas, Matplotlib, Seaborn)
- Microsoft Excel (Pivot Tables, Charts)

## Dataset
Supermarket Sales dataset with 1000 transactions across 
3 branches in Myanmar (Yangon, Mandalay, Naypyitaw)

## Key Insights
1. Sports and Travel is most price sensitive with elasticity of -13.45, indicating strong customer response to price changes
2. Fashion Accessories is inelastic at -0.19 — safe to raise prices
3. Branch C in Naypyitaw generates highest revenue of $110,568, indicating strong regional performance
4. 5% discount on elastic categories projects significant revenue gain

## Project Structure
- pricing_analysis.py — Main Python analysis file
- supermarket_sales.xlsx — Cleaned Excel file with pivot tables
- demand_elasticity.png — Demand elasticity visualization
- total_revenue.png — Branch revenue comparison
- discount_impact.png — Projected discount impact chart

## How to Run
1. Install required libraries:
pip install pandas matplotlib seaborn openpyxl
2. Run the analysis:
python pricing_analysis.py
