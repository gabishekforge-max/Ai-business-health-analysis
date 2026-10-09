def generate_risks_and_recommendations(df, kpis):
    risks = []
    recommendations = []

    if kpis['profit_margin'] < 10:
        risks.append({'severity': 'HIGH', 'title': 'Low Profit Margin', 'desc': f"Overall margin is low ({kpis['profit_margin']:.1f}%)."})
        recommendations.append("Review cost structures and raise prices on low-margin products.")

    low_stock = df[df['Stock'] < 10]['Product'].unique()
    if len(low_stock) > 0:
        products_str = ", ".join(low_stock[:3])
        risks.append({'severity': 'HIGH', 'title': 'Low Stock Alert', 'desc': f"Low stock (<10 units) for: {products_str}."})
        recommendations.append(f"Restock high-demand items immediately: {products_str}.")

    overstock = df[df['Stock'] > 100]['Product'].unique()
    if len(overstock) > 0:
        products_str = ", ".join(overstock[:3])
        risks.append({'severity': 'MEDIUM', 'title': 'Overstocked Inventory', 'desc': f"High inventory tied up in: {products_str}."})
        recommendations.append(f"Consider running promotional sales for overstocked items: {products_str}.")

    cat_rev = df.groupby('Category')['Revenue'].sum()
    if not cat_rev.empty:
        top_cat = cat_rev.idxmax()
        top_cat_share = (cat_rev.max() / kpis['total_revenue']) * 100
        if top_cat_share > 60:
            risks.append({'severity': 'MEDIUM', 'title': 'High Category Dependency', 'desc': f"Category '{top_cat}' contributes {top_cat_share:.1f}% of revenue."})
            recommendations.append(f"Diversify product line beyond {top_cat} to minimize sector dependence.")

    if not risks:
        risks.append({'severity': 'LOW', 'title': 'Stable Operations', 'desc': 'No critical short-term operational risks detected.'})
        recommendations.append("Maintain current operational performance and monitor sales trends weekly.")

    return risks, recommendations