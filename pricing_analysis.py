import pandas as pd
df = pd.read_csv('supermarket_sales - Sheet1 (1).csv') 
print(df.head())
print("Rows and Columns:", df.shape)
print("Columns:", df.columns.tolist())
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M')
# print(df.dtypes)
# print("\nMissing Values")
# print(df.isnull().sum())
monthly_data = df.groupby(['Product line', 'Month']).agg(
    avg_price=('Unit price', 'mean'),
    total_quantity=('Quantity', 'sum')
).reset_index()
print("Monthly data per category:")
print(monthly_data)
monthly_data['price_pct_change'] = monthly_data.groupby(
    'Product line')['avg_price'].pct_change()

monthly_data['quantity_pct_change'] = monthly_data.groupby(
    'Product line')['total_quantity'].pct_change()
# print(monthly_data['price_pct_change'])
# quantity % change divided by price % change
monthly_data['elasticity'] = (
    monthly_data['quantity_pct_change'] /
    monthly_data['price_pct_change']
)

final_elasticity = monthly_data.groupby(
    'Product line')['elasticity'].mean().reset_index()

final_elasticity.columns = ['Product line', 'avg_elasticity']

print("Final Elasticity per Product Line:")
print(final_elasticity)
print("=" * 55)
print("   PRICING RECOMMENDATIONS FOR YOUR SUPERMARKET")
print("=" * 55)

for index, row in final_elasticity.iterrows():
    category = row['Product line']
    elasticity = row['avg_elasticity']
    
    if elasticity > 0:
        signal = "UNUSUAL - other factors driving sales"
        action = "Investigate promotions or seasonality"
        emoji = "🤔"
    elif elasticity > -1:
        signal = "INELASTIC - customers not price sensitive"
        action = "Safe to raise prices slightly"
        emoji = "✅"
    elif elasticity > -5:
        signal = "ELASTIC - customers are price sensitive"
        action = "Consider discounts to boost volume"
        emoji = "📉"
    else:
        signal = "HIGHLY ELASTIC - extremely price sensitive"
        action = "Never raise prices here!"
        emoji = "🚨"
    
    # Print a clean summary for each category
    print(f"\n{emoji} {category}")
    print(f"   Elasticity  : {elasticity:.2f}")
    print(f"   Behaviour   : {signal}")
    print(f"   Recommended : {action}")

print("\n" + "=" * 55)

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))

final_elasticity = final_elasticity.sort_values('avg_elasticity')

sns.barplot(
    data=final_elasticity,
    x='avg_elasticity',
    y='Product line',
    hue='avg_elasticity',
    palette='coolwarm',
    legend=False
)
# Bars left of this line = negative elasticity = price sensitive
# Bars right of this line = positive elasticity = unusual
plt.axvline(x=0, color='black', linestyle='--', linewidth=1)
plt.title('Demand Elasticity by Product Line', fontsize=14)
plt.xlabel('Average Elasticity Value\n(negative = price sensitive, positive = unusual)')
plt.ylabel('Product Line')
plt.tight_layout()
plt.savefig('demand_elasticity.png', bbox_inches='tight')
plt.close()

print("\nChart saved as demand_elasticity.png!")
# plt.show()

branch_data = df.groupby('Branch').agg(
    avg_price=('Unit price', 'mean'),
    total_revenue=('Total', 'sum'),
    total_quantity=('Quantity', 'sum')
).reset_index()

print("Branch Comparison:")
print(branch_data)
print()
branch_product = df.groupby(
    ['Branch', 'Product line']).agg(
    avg_price=('Unit price', 'mean')
).reset_index()

print("Price per Product per Branch:")
print(branch_product.to_string())
print()
# branch revenue comparison
plt.figure(figsize=(8, 5))

sns.barplot(
    data=branch_data,
    x='Branch',
    y='total_revenue',
    hue='Branch',
    palette='Set2',
    legend=False
)

plt.title('Total Revenue by Branch', fontsize=14)
plt.xlabel('Branch')
plt.ylabel('Total Revenue (USD)')
plt.tight_layout()
plt.savefig('total_revenue.png', bbox_inches='tight')
plt.close()

print("\nChart saved as total_revenue.png!")
# plt.show()
# category wise price comparison across branches
plt.figure(figsize=(12, 6))

sns.barplot(
    data=branch_product,
    x='Product line',
    y='avg_price',
    hue='Branch',
    palette='Set2'
)

plt.title('Average Price per Product Line by Branch', fontsize=14)
plt.xlabel('Product Line')
plt.ylabel('Average Unit Price (USD)')

plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('average_price_per_branch.png', bbox_inches='tight')
plt.close()

print("\nChart saved as average_price_per_branch.png!")
# plt.show()
print("Branch Revenue Ranking:")
print(branch_data.sort_values('total_revenue', ascending=False))

print(df.groupby(['Branch', 'City']).size().reset_index(name="count"))

base_data = df.groupby('Product line').agg(
    avg_price=('Unit price', 'mean'),
    total_quantity=('Quantity', 'sum'),
    total_revenue=('Total', 'sum')
).reset_index()
simulation = base_data.merge(
    final_elasticity,
    on='Product line'
)

print("Base Data for Simulation:")
print(simulation)
print()

discount_rate = 0.05  # 5% discount

# new_price = old_price × (1 - discount_rate)
# for example 100 × (1 - 0.05) = 100 × 0.95 = 95
simulation['new_price'] = simulation.apply(
    lambda row: row['avg_price'] * (1 - discount_rate)
    if abs(row['avg_elasticity']) > 1
    else row['avg_price'],
    axis=1
)


# % change in quantity = elasticity × % change in price
# new_quantity = old_quantity × (1 + elasticity × discount_rate)
# The minus sign in elasticity means quantity goes UP when price goes DOWN
simulation['new_quantity'] = simulation.apply(
    lambda row: row['total_quantity'] * (
        1 + row['avg_elasticity'] * (-discount_rate))
    if abs(row['avg_elasticity']) > 1
    else row['total_quantity'],
    axis=1
)

simulation['new_revenue'] = (
    simulation['new_price'] * simulation['new_quantity']
)

simulation['revenue_impact'] = (
    simulation['new_revenue'] - simulation['total_revenue']
)

print("Discount Simulation Results:")
print(simulation[[
    'Product line',
    'total_revenue',
    'new_revenue',
    'revenue_impact'
]].to_string())
print()

print("=" * 60)
print("   FINAL PRICING AND DISCOUNT RECOMMENDATIONS")
print("=" * 60)

total_impact = 0

for index, row in simulation.iterrows():
    category = row['Product line']
    old_rev = row['total_revenue']
    new_rev = row['new_revenue']
    impact = row['revenue_impact']
    elasticity = row['avg_elasticity']
    total_impact += impact

    if abs(elasticity) <= 1 and elasticity < 0:
        print(f"\n✅ {category}")
        print(f"   Action    : Raise prices by 5%")
        print(f"   Current revenue : ${old_rev:,.2f}")
        print(f"   No discount applied — inelastic category")

    elif elasticity > 0:
        print(f"\n🤔 {category}")
        print(f"   Action    : Investigate seasonality first")
        print(f"   Current revenue : ${old_rev:,.2f}")
        print(f"   No discount applied — unusual behaviour")

    else:
        print(f"\n📉 {category}")
        print(f"   Action    : Apply 5% discount")
        print(f"   Current revenue : ${old_rev:,.2f}")
        print(f"   Projected revenue : ${new_rev:,.2f}")
        if impact > 0:
            print(f"   Revenue GAIN : +${impact:,.2f} ✅")
        else:
            print(f"   Revenue LOSS : ${impact:,.2f} ⚠️")

print(f"\n{'=' * 60}")
print(f"   TOTAL PROJECTED REVENUE IMPACT: ${total_impact:,.2f}")
print(f"{'=' * 60}")

plt.figure(figsize=(10, 6))

# Color bars green if positive impact, red if negative
colors = [
    'green' if x > 0 else 'red'
    for x in simulation['revenue_impact']
]

plt.bar(
    simulation['Product line'],
    simulation['revenue_impact'],
    color=colors
)

plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
plt.title('Projected Revenue Impact of 5% Discount Strategy',
          fontsize=14)
plt.xlabel('Product Line')
plt.ylabel('Revenue Impact (USD)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
# plt.show()
plt.savefig('discount_impact.png', bbox_inches='tight')
plt.close()

print("\nChart saved as discount_impact.png!")