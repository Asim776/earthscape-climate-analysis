from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from data_processing.utils import load_dataset, detect_anomalies, train_models, make_prediction
import numpy as np
from datetime import datetime

@login_required
def dashboard_view(request):
    # 🔹 Load FULL dataset (for global stats)
    df_all = load_dataset()
    df_all = detect_anomalies(df_all)

    # 🔹 Copy for filtering
    df = df_all.copy()

    # ✅ GET FILTER VALUES
    selected_year = request.GET.get('year')
    selected_region = request.GET.get('region')

    # ✅ APPLY FILTERS
    if selected_year:
        df = df[df['Year'] == int(selected_year)]

    if selected_region:
        df = df[df['Region'] == selected_region]

    # ✅ DROPDOWNS (ALWAYS from FULL dataset)
    years = sorted(df_all['Year'].unique())
    regions = sorted(df_all['Region'].unique())

    # ✅ CHART DATA
    dates = (df['Year'].astype(str) + "-" + df['Month'].astype(str)).tolist()[:12]
    temps = df['temperature'].tolist()[:12]

    # ✅ FILTERED STATS
    total_records = len(df)
    anomalies_count = df['anomaly'].sum()

    # ✅ FULL DATA STATS (NEW 🔥)
    total_records_all = len(df_all)
    total_anomalies_all = df_all['anomaly'].sum()

    # ✅ ANOMALY TABLE
    anomaly_data = df[df['anomaly'] == 1][
        ['Year', 'Month', 'Region', 'temperature', 'humidity', 'co2', 'rainfall']
    ].head(10).to_dict(orient='records')

    # ✅ CONTEXT
    context = {
        'dates': dates,
        'temps': temps,

        # FILTERED
        'total_records': total_records,
        'anomalies_count': anomalies_count,

        # FULL DATA (🔥 NEW)
        'total_records_all': total_records_all,
        'total_anomalies_all': total_anomalies_all,

        'avg_temp': round(df['temperature'].mean(), 2),
        'anomaly_data': anomaly_data,

        # FILTERS
        'years': years,
        'regions': regions,
        'selected_year': selected_year,
        'selected_region': selected_region
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def analysis_view(request):
    df = load_dataset()

    # Filters
    selected_year = request.GET.get('year')
    selected_region = request.GET.get('region')

    if selected_year:
        df = df[df['Year'] == int(selected_year)]

    if selected_region:
        df = df[df['Region'] == selected_region]

    # Dropdowns (UNFILTERED)
    df_all = load_dataset()
    years = sorted(df_all['Year'].unique())
    regions = sorted(df_all['Region'].unique())

    # Stats
    avg_temp = round(df['temperature'].mean(), 2)
    max_temp = df['temperature'].max()
    min_temp = df['temperature'].min()

    # Monthly aggregation
    monthly = df.groupby('Month').agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'co2': 'mean',
        'rainfall': 'mean'
    }).reset_index()

    months = monthly['Month'].tolist()
    temps = monthly['temperature'].round(2).tolist()
    humidity = monthly['humidity'].round(2).tolist()
    co2 = monthly['co2'].round(2).tolist()
    rainfall = monthly['rainfall'].round(2).tolist()

    context = {
        'avg_temp': avg_temp,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'months': months,
        'temps': temps,
        'humidity': humidity,
        'co2': co2,
        'rainfall': rainfall,
        'years': years,
        'regions': regions,
        'selected_year': selected_year,
        'selected_region': selected_region
    }

    return render(request, 'dashboard/analysis.html', context)



@login_required
def charts_view(request):
    df = load_dataset()

    # Basic
    months = df['Month'].tolist()[:12]
    temps = df['temperature'].tolist()[:12]
    humidity = df['humidity'].tolist()[:12]
    co2 = df['co2'].tolist()[:12]
    rainfall = df['rainfall'].tolist()[:12]

    # 🥧 FIXED PIE DATA
    region_data = df.groupby('Region')['rainfall'].mean().reset_index()
    regions = region_data['Region'].tolist()
    rainfall_avg = region_data['rainfall'].round(2).tolist()

    # 🔥 HEATMAP
    heatmap_data = df.pivot_table(
        index='Region',
        columns='Month',
        values='temperature',
        aggfunc='mean'
    ).fillna(0)

    # Correlation
    corr = df[['temperature', 'humidity', 'co2', 'rainfall']].corr()

    context = {
        'months': months,
        'temps': temps,
        'humidity': humidity,
        'co2': co2,
        'rainfall': rainfall,

        # ✅ FIXED
        'regions': regions,
        'rainfall_avg': rainfall_avg,

        'heatmap_values': heatmap_data.values.tolist(),
        'heatmap_x': heatmap_data.columns.tolist(),
        'heatmap_y': heatmap_data.index.tolist(),

        'corr_values': corr.values.tolist(),
        'corr_labels': corr.columns.tolist(),

        'box_temp': df['temperature'].tolist(),
        'box_humidity': df['humidity'].tolist(),
        'box_co2': df['co2'].tolist(),
        'box_rainfall': df['rainfall'].tolist()
    }

    return render(request, 'dashboard/charts.html', context)




@login_required
def predictions_view(request):
    df = load_dataset()
    models = train_models(df)

    prediction = None
    accuracy = None

    # ✅ AUTO SELECT BEST MODEL
    best_model_name = max(models, key=lambda k: models[k][1])
    model, accuracy = models[best_model_name]

    # 🔥 FUTURE YEARS (next 10 years)
    current_year = datetime.now().year
    future_years = list(range(current_year, current_year + 10))

    # 🔥 MONTHS
    months_list = list(range(1, 13))

    if request.method == 'POST':
        try:
            # ✅ ONLY YEAR & MONTH FROM USER
            year = int(request.POST.get('year'))
            month = int(request.POST.get('month'))

            # 🚫 BLOCK PAST YEARS
            if year < current_year:
                prediction = None
            else:
                # 🔥 AUTO-GENERATE FEATURES (REAL WORLD LOGIC)

                # Use dataset averages
                co2 = df['co2'].mean()
                humidity = df['humidity'].mean()
                rainfall = df['rainfall'].mean()

                # (Optional: slight future trend simulation)
                co2 += (year - current_year) * 2   # CO2 increases yearly
                humidity += (month % 3) * 0.5      # small variation
                rainfall += (month % 4) * 1.2      # seasonal variation

                prediction = make_prediction(model, co2, humidity, rainfall, year, month)

        except Exception as e:
            print("Prediction Error:", e)
            prediction = None

    # 📊 HISTORICAL TREND
    monthly_avg = df.groupby('Month')['temperature'].mean().reset_index()

    months = monthly_avg['Month'].astype(str).tolist()
    temps = monthly_avg['temperature'].round(2).tolist()

    # ➕ Add prediction point
    if prediction:
        months.append("Future")
        temps.append(prediction)

    context = {
        'prediction': prediction,
        'accuracy': round(accuracy * 100, 2),

        'years': future_years,
        'months_list': months_list,

        'months': months,
        'temps': temps
    }

    return render(request, 'dashboard/predictions.html', context)