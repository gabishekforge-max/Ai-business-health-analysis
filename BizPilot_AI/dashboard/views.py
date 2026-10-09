import os
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.conf import settings

from .forms import CSVUploadForm
from .models import AnalysisResult
from .data_processor import process_business_csv
from .ml_engine import calculate_kpis, calculate_health_score, predict_sales_forecast
from .recommendations import generate_risks_and_recommendations


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to BizPilot AI.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def _prepare_analysis_context(request, df, filename):
    kpis = calculate_kpis(df)
    score, status, explanation = calculate_health_score(kpis, df)
    forecast = predict_sales_forecast(df)
    risks, recommendations = generate_risks_and_recommendations(df, kpis)

    top_products = df.groupby('Product').agg({'Revenue': 'sum', 'Quantity': 'sum', 'Profit': 'sum'}).reset_index()
    top_products = top_products.sort_values(by='Revenue', ascending=False).to_dict('records')

    low_products = df.groupby('Product').agg({'Revenue': 'sum', 'Profit': 'sum'}).reset_index()
    low_products = low_products.sort_values(by='Revenue', ascending=True).head(5).to_dict('records')

    inventory = df.groupby('Product')['Stock'].last().reset_index().to_dict('records')
    for idx, item in enumerate(inventory):
        if item['Stock'] < 10:
            inventory[idx]['status'] = 'Low Stock'
            inventory[idx]['badge'] = 'danger'
        elif item['Stock'] > 100:
            inventory[idx]['status'] = 'Overstock'
            inventory[idx]['badge'] = 'warning'
        else:
            inventory[idx]['status'] = 'Healthy Stock'
            inventory[idx]['badge'] = 'success'

    rev_time = df.groupby(df['Date'].dt.strftime('%Y-%m-%d'))['Revenue'].sum().to_dict()
    prof_time = df.groupby(df['Date'].dt.strftime('%Y-%m-%d'))['Profit'].sum().to_dict()
    cat_sales = df.groupby('Category')['Revenue'].sum().to_dict()
    cat_margin = df.groupby('Category')['Profit_Margin'].mean().to_dict()
    prod_rev = df.groupby('Product')['Revenue'].sum().head(5).to_dict()
    prod_stock = df.groupby('Product')['Stock'].last().head(5).to_dict()

    AnalysisResult.objects.create(
        user=request.user,
        filename=filename,
        total_revenue=kpis['total_revenue'],
        total_profit=kpis['total_profit'],
        profit_margin=kpis['profit_margin'],
        health_score=score,
        health_status=status,
        total_products=kpis['total_products'],
        total_records=len(df)
    )

    context = {
        'kpis': kpis,
        'health_score': score,
        'health_status': status,
        'health_explanation': explanation,
        'forecast': forecast,
        'risks': risks,
        'recommendations': recommendations,
        'top_products': top_products,
        'low_products': low_products,
        'inventory': inventory,
        'chart_rev_time': {'labels': list(rev_time.keys()), 'values': list(rev_time.values())},
        'chart_prof_time': {'labels': list(prof_time.keys()), 'values': list(prof_time.values())},
        'chart_cat_sales': {'labels': list(cat_sales.keys()), 'values': list(cat_sales.values())},
        'chart_cat_margin': {'labels': list(cat_margin.keys()), 'values': [round(v, 2) for v in cat_margin.values()]},
        'chart_prod_rev': {'labels': list(prod_rev.keys()), 'values': list(prod_rev.values())},
        'chart_prod_stock': {'labels': list(prod_stock.keys()), 'values': list(prod_stock.values())},
    }

    request.session['current_analysis'] = context
    return context


@login_required
def dashboard_view(request):
    context = request.session.get('current_analysis')
    if not context:
        sample_path = os.path.join(settings.BASE_DIR, 'sample_data', 'sample_business_data.csv')
        if os.path.exists(sample_path):
            df, error = process_business_csv(sample_path)
            if not error:
                context = _prepare_analysis_context(request, df, "sample_business_data.csv")
    return render(request, 'dashboard/dashboard.html', context or {})


@login_required
def upload_view(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Invalid file format. Please upload a .csv file.")
                return render(request, 'dashboard/upload.html', {'form': form})

            df, error = process_business_csv(csv_file)
            if error:
                messages.error(request, error)
            else:
                _prepare_analysis_context(request, df, csv_file.name)
                messages.success(request, "Data uploaded and processed successfully!")
                return redirect('dashboard')
    else:
        form = CSVUploadForm()
    return render(request, 'dashboard/upload.html', {'form': form})


@login_required
def load_sample_data(request):
    sample_path = os.path.join(settings.BASE_DIR, 'sample_data', 'sample_business_data.csv')
    if os.path.exists(sample_path):
        df, error = process_business_csv(sample_path)
        if not error:
            _prepare_analysis_context(request, df, "sample_business_data.csv")
            messages.success(request, "Loaded demo sample data successfully!")
        else:
            messages.error(request, error)
    else:
        messages.error(request, "Sample data file not found.")
    return redirect('dashboard')


@login_required
def download_sample_csv(request):
    sample_path = os.path.join(settings.BASE_DIR, 'sample_data', 'sample_business_data.csv')
    if os.path.exists(sample_path):
        return FileResponse(open(sample_path, 'rb'), as_attachment=True, filename='sample_business_data.csv')
    return HttpResponse("File not found", status=404)


@login_required
def analysis_view(request):
    context = request.session.get('current_analysis', {})
    return render(request, 'dashboard/analysis.html', context)


@login_required
def recommendations_view(request):
    context = request.session.get('current_analysis', {})
    return render(request, 'dashboard/recommendations.html', context)


@login_required
def history_view(request):
    history = AnalysisResult.objects.filter(user=request.user).order_by('-upload_date')
    return render(request, 'dashboard/history.html', {'history': history})