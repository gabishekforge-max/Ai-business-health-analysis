import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def calculate_kpis(df):
    total_revenue = float(df['Revenue'].sum())
    total_profit = float(df['Profit'].sum())
    total_units_sold = int(df['Quantity'].sum())
    avg_order_value = float(df['Revenue'].mean()) if len(df) > 0 else 0.0
    profit_margin = float((total_profit / total_revenue * 100)) if total_revenue > 0 else 0.0
    total_inventory = int(df['Stock'].sum())
    total_products = int(df['Product'].nunique())

    return {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'total_units_sold': total_units_sold,
        'avg_order_value': avg_order_value,
        'total_inventory': total_inventory,
        'total_products': total_products
    }

def calculate_health_score(kpis, df):
    score = 0
    pm = kpis['profit_margin']
    if pm >= 25: score += 30
    elif pm >= 15: score += 20
    elif pm >= 5: score += 10
    else: score += 5

    if kpis['total_revenue'] > 100000: score += 25
    elif kpis['total_revenue'] > 50000: score += 15
    else: score += 10

    low_stock_count = len(df[df['Stock'] < 10])
    if low_stock_count == 0: score += 25
    elif low_stock_count <= 2: score += 15
    else: score += 5

    if kpis['total_products'] >= 5: score += 20
    elif kpis['total_products'] >= 2: score += 10
    else: score += 5

    score = min(max(score, 0), 100)

    if score >= 80: status = "Excellent"
    elif score >= 60: status = "Good"
    elif score >= 40: status = "Average"
    elif score >= 20: status = "Poor"
    else: status = "Critical"

    explanation = f"Business is performing at {status} level based on a {pm:.1f}% profit margin and inventory status."
    return score, status, explanation

def predict_sales_forecast(df):
    df_daily = df.groupby('Date')['Revenue'].sum().reset_index()
    df_daily = df_daily.sort_values('Date')

    if len(df_daily) < 3:
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in df_daily['Date']],
            'historical': df_daily['Revenue'].tolist(),
            'forecast_dates': [],
            'forecast': [],
            'error': "Not enough date points for accurate ML forecasting."
        }

    df_daily['Day'] = (df_daily['Date'] - df_daily['Date'].min()).dt.days
    X = df_daily[['Day']].values
    y = df_daily['Revenue'].values

    model = LinearRegression()
    model.fit(X, y)

    last_day = df_daily['Day'].max()
    future_days = np.array([[last_day + i] for i in range(1, 8)])
    predictions = model.predict(future_days)
    predictions = np.maximum(predictions, 0)

    last_date = df_daily['Date'].max()
    future_dates = [(last_date + pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]

    return {
        'dates': [d.strftime('%Y-%m-%d') for d in df_daily['Date']],
        'historical': [round(v, 2) for v in y],
        'forecast_dates': future_dates,
        'forecast': [round(v, 2) for v in predictions],
        'error': None
    }