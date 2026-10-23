import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Zarkhez Zameen AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM DESIGN

st.markdown("""
<style>
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(120, 150, 120, 0.2);
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(120deg, #123c2c, #26734d);
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white;
        font-size: 2.3rem;
        margin-bottom: 8px;
    }

    .hero p {
        color: #e3f4e8;
        font-size: 1rem;
    }

    .section-note {
        color: #6b7f70;
        font-size: 0.92rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(120, 150, 120, 0.25);
        padding: 16px;
        border-radius: 12px;
        background: rgba(100, 150, 100, 0.04);
    }

    .footer {
        text-align: center;
        padding: 16px 0;
        color: #748477;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# LANGUAGE
if "language" not in st.session_state:
    st.session_state.language = "English"

language = st.sidebar.selectbox(
    "🌐 Language / زبان",
    ["English", "اردو"],
    index=0 if st.session_state.language == "English" else 1
)

st.session_state.language = language
URDU = language == "اردو"


TEXT = {
    "farm": ("Farm Configuration", "کھیت کی تفصیلات"),
    "city": ("City", "شہر"),
    "crop": ("Crop", "فصل"),
    "area": ("Field area (acres)", "کھیت کا رقبہ (ایکڑ)"),
    "soil": ("Soil type", "مٹی کی قسم"),
    "moisture": ("Soil moisture (%)", "مٹی میں نمی (%)"),
    "weather": ("Weather & Forecast", "موسم اور پیش گوئی"),
    "fetch": ("Fetch Live Weather", "موجودہ موسم معلوم کریں"),
    "temp": ("Temperature (°C)", "درجہ حرارت (°C)"),
    "rain": ("Forecast rainfall (mm)", "متوقع بارش (ملی میٹر)"),
    "dashboard": ("Irrigation Dashboard", "آبپاشی ڈیش بورڈ"),
    "water": ("Estimated Water Need", "پانی کی اندازاً ضرورت"),
    "depth": ("Water Depth", "پانی کی گہرائی"),
    "chart": ("Water Requirement Comparison", "پانی کی ضرورت کا موازنہ"),
    "alerts": ("Farm Alerts", "کھیت کے انتباہات"),
    "recommend": ("Smart Recommendations", "سمارٹ تجاویز"),
    "report": ("Download Farm Report", "کھیت کی رپورٹ ڈاؤن لوڈ کریں"),
    "baseline": ("Baseline Estimate", "بنیادی اندازہ"),
    "adjusted": ("Adjusted Estimate", "ترمیم شدہ اندازہ"),
}


def tr(key):
    return TEXT[key][1] if URDU else TEXT[key][0]

# HEADER

st.markdown("""
<div class="hero">
    <h1> Zarkhez Zameen AI</h1>
    <p>Smart Irrigation | Weather Insights | Farm Monitoring</p>
    <p>Smarter decisions for a more sustainable farm.</p>
</div>
""", unsafe_allow_html=True)


# CROP AND SOIL DATA

CROP_DATA = {
    "Wheat": 0.85,
    "Rice": 1.10,
    "Cotton": 0.90,
    "Maize": 0.95,
    "Sugarcane": 1.15,
    "Vegetables": 1.00
}

CROP_URDU = {
    "Wheat": "گندم",
    "Rice": "چاول",
    "Cotton": "کپاس",
    "Maize": "مکئی",
    "Sugarcane": "گنا",
    "Vegetables": "سبزیاں"
}

SOIL_ADJUSTMENT = {
    "Sandy": 1.15,
    "Loamy": 1.00,
    "Clay": 0.90
}

SOIL_URDU = {
    "Sandy": "ریتلی",
    "Loamy": "دومی",
    "Clay": "چکنی"
}


def display_crop(crop):
    return CROP_URDU[crop] if URDU else crop


def display_soil(soil):
    return SOIL_URDU[soil] if URDU else soil


# WEATHER SERVICE

def get_weather(city):
    try:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=15
        )
        geo_response.raise_for_status()

        locations = geo_response.json().get("results", [])

        if not locations:
            return None, "City not found."

        place = locations[0]

        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m",
                "daily": "precipitation_sum",
                "forecast_days": 1,
                "timezone": "auto"
            },
            timeout=15
        )
        response.raise_for_status()

        data = response.json()

        weather = {
            "city": place["name"],
            "temperature": float(
                data["current"]["temperature_2m"]
            ),
            "rainfall": float(
                data["daily"]["precipitation_sum"][0]
            )
        }

        return weather, None

    except requests.RequestException:
        return None, "Could not connect to the weather service."

    except (KeyError, IndexError, ValueError, TypeError):
        return None, "Weather data was incomplete."

# IRRIGATION CALCULATOR

def calculate_irrigation(
    crop, area, soil, moisture, temperature, rainfall
):
    # Formulation, It is not a validated agricultural model.

    crop_factor = CROP_DATA[crop]
    soil_factor = SOIL_ADJUSTMENT[soil]

    temperature_factor = max(
        0.5,
        min(1.5, 1 + (temperature - 25) * 0.02)
    )

    base_depth = (
        4.0 * crop_factor * soil_factor * temperature_factor
    )

    moisture_factor = max(
        0.0,
        min(1.0, (100 - moisture) / 70)
    )

    effective_rain = max(0, rainfall) * 0.7

    net_depth = max(
        0,
        base_depth * moisture_factor - effective_rain
    )

    irrigation_efficiency = 0.75

    adjusted_depth = net_depth / irrigation_efficiency

    litres_per_mm_acre = 4046.86

    adjusted_litres = (
        adjusted_depth * area * litres_per_mm_acre
    )

    baseline_litres = (
        base_depth * area * litres_per_mm_acre
        / irrigation_efficiency
    )

    return {
        "adjusted": adjusted_litres,
        "baseline": baseline_litres,
        "depth": adjusted_depth,
        "difference": max(
            0, baseline_litres - adjusted_litres
        )
    }


# SIDEBAR: FARM INPUTS

st.sidebar.header( tr("farm"))

city = st.sidebar.text_input(
    tr("city"),
    value="Hyderabad"
)

crop = st.sidebar.selectbox(
    tr("crop"),
    list(CROP_DATA.keys()),
    format_func=display_crop
)

area = st.sidebar.number_input(
    tr("area"),
    min_value=0.1,
    max_value=10000.0,
    value=1.0,
    step=0.1
)

soil = st.sidebar.selectbox(
    tr("soil"),
    list(SOIL_ADJUSTMENT.keys()),
    format_func=display_soil
)

moisture = st.sidebar.slider(
    tr("moisture"),
    min_value=0,
    max_value=100,
    value=40
)


# WEATHER CONTROLS

st.sidebar.divider()
st.sidebar.subheader( tr("weather"))

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

if "weather_error" not in st.session_state:
    st.session_state.weather_error = None

if st.sidebar.button("🌐 " + tr("fetch"), use_container_width=True):
    with st.spinner("Fetching weather..."):
        weather_data, weather_error = get_weather(city)

    st.session_state.weather_data = weather_data
    st.session_state.weather_error = weather_error

weather = st.session_state.weather_data

if weather and weather.get("city", "").lower() == city.strip().lower():
    temperature = weather["temperature"]
    rainfall = weather["rainfall"]

    st.sidebar.success(
        f"{weather['city']} · {temperature:.1f} °C"
    )

    st.sidebar.write(
        f"{tr('rain')}: {rainfall:.1f} mm"
    )

else:
    temperature = st.sidebar.number_input(
        tr("temp"),
        min_value=-10.0,
        max_value=60.0,
        value=30.0
    )

    rainfall = st.sidebar.number_input(
        tr("rain"),
        min_value=0.0,
        max_value=500.0,
        value=0.0
    )

    if st.session_state.weather_error:
        st.sidebar.warning(st.session_state.weather_error)

    st.sidebar.caption(
        "Manual weather inputs are being used."
        if not URDU
        else "موسم کی قدریں دستی طور پر استعمال ہو رہی ہیں۔"
    )

# DASHBOARD METRICS

st.header( tr("dashboard"))

st.caption(
    "Review your field inputs and the illustrative water estimate."
    if not URDU
    else "کھیت کی معلومات اور پانی کے اندازے کا جائزہ لیں۔"
)

result = calculate_irrigation(
    crop,
    area,
    soil,
    moisture,
    temperature,
    rainfall
)

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    tr("water"),
    f"{result['adjusted']:,.0f} L"
)

m2.metric(
    tr("depth"),
    f"{result['depth']:.2f} mm"
)

m3.metric(
    "Temperature",
    f"{temperature:.1f} °C"
)

m4.metric(
    "Rainfall",
    f"{rainfall:.1f} mm"
)

st.caption(
    f" {city}  |{display_crop(crop)}  |  "
    f" {display_soil(soil)}  |  "
    f" {area:.1f} acres"
)

# CHARTS

st.divider()
st.subheader( tr("chart"))

chart_df = pd.DataFrame({
    "Estimate": [
        tr("baseline"),
        tr("adjusted")
    ],
    "Water (litres)": [
        result["baseline"],
        result["adjusted"]
    ]
})

fig = px.bar(
    chart_df,
    x="Estimate",
    y="Water (litres)",
    color="Estimate",
    text_auto=".2s",
    color_discrete_sequence=[
        "#8BC34A",
        "#168C75"
    ]
)

fig.update_layout(
    template="plotly_white",
    showlegend=False,
    height=400,
    xaxis_title="",
    yaxis_title="Water (litres)",
    margin=dict(l=20, r=20, t=35, b=20)
)

fig.update_traces(
    textposition="outside",
    marker_line_width=0
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "The baseline is a comparison estimate, not measured water savings."
    if not URDU
    else "بنیادی اندازہ موازنہ کے لیے ہے، پانی کی حقیقی بچت کی پیمائش نہیں۔"
)

st.divider()
st.header( tr("alerts"))

alerts = []

if moisture < 25:
    alerts.append((
        "warning",
        "Low soil moisture input. Check field conditions."
        if not URDU
        else "مٹی میں نمی کم درج کی گئی ہے۔ کھیت کی حالت چیک کریں۔"
    ))

elif moisture > 80:
    alerts.append((
        "warning",
        "High soil moisture input. Check drainage before watering."
        if not URDU
        else "مٹی میں نمی زیادہ ہے۔ پانی دینے سے پہلے نکاسی چیک کریں۔"
    ))

else:
    alerts.append((
        "success",
        "Moisture input is within the app's middle range."
        if not URDU
        else "درج کردہ نمی ایپ کی درمیانی حد میں ہے۔"
    ))

if rainfall >= 5:
    alerts.append((
        "info",
        "Rain is forecast. Recheck actual field conditions."
        if not URDU
        else "بارش متوقع ہے۔ کھیت کی حقیقی حالت دوبارہ چیک کریں۔"
    ))

if temperature >= 38:
    alerts.append((
        "warning",
        "High temperature. Check crops for heat stress."
        if not URDU
        else "درجہ حرارت زیادہ ہے۔ فصل پر گرمی کے اثرات چیک کریں۔"
    ))

for level, message in alerts:
    if level == "warning":
        st.warning( message)

    elif level == "success":
        st.success( message)

    else:
        st.info( message)


# RECOMMENDATIONS

st.subheader( tr("recommend"))

if moisture >= 80:
    recommendation = (
        "Check soil and drainage before deciding whether to irrigate."
        if not URDU
        else "آبپاشی کا فیصلہ کرنے سے پہلے مٹی اور نکاسی چیک کریں۔"
    )

elif rainfall >= 5:
    recommendation = (
        "Recheck actual rainfall and soil moisture before watering."
        if not URDU
        else "پانی دینے سے پہلے حقیقی بارش اور مٹی کی نمی چیک کریں۔"
    )

elif moisture < 25:
    recommendation = (
        "Inspect the crop and soil. Seek local advice if needed."
        if not URDU
        else "فصل اور مٹی چیک کریں۔ ضرورت ہو تو مقامی زرعی مشورہ لیں۔"
    )

elif temperature >= 38:
    recommendation = (
        "Monitor crops during hot conditions and follow local guidance."
        if not URDU
        else "گرم موسم میں فصل کی نگرانی کریں اور مقامی مشورے پر عمل کریں۔"
    )

else:
    recommendation = (
        "Compare this estimate with crop stage and local agricultural advice."
        if not URDU
        else "اس اندازے کا فصل کی نشوونما اور مقامی زرعی مشورے سے موازنہ کریں۔"
    )

st.info( recommendation)

# DOWNLOAD REPORT

st.divider()
st.header( tr("report"))

report = pd.DataFrame([
    {"Item": "City", "Value": city},
    {"Item": "Crop", "Value": crop},
    {"Item": "Area (acres)", "Value": area},
    {"Item": "Soil type", "Value": soil},
    {"Item": "Soil moisture (%)", "Value": moisture},
    {"Item": "Temperature (C)", "Value": temperature},
    {"Item": "Forecast rainfall (mm)", "Value": rainfall},
    {
        "Item": "Estimated water (litres)",
        "Value": round(result["adjusted"], 2)
    },
    {
        "Item": "Baseline estimate (litres)",
        "Value": round(result["baseline"], 2)
    },
    {
        "Item": "Estimated difference (litres)",
        "Value": round(result["difference"], 2)
    }
])

st.download_button(
    label= tr("report"),
    data=report.to_csv(
        index=False
    ).encode("utf-8-sig"),
    file_name="zarkhez_zameen_farm_report.csv",
    mime="text/csv",
    use_container_width=True
)


# DISCLAIMER AND FOOTER
st.divider()

st.warning(
    "Educational prototype only. The irrigation formula is simplified "
    "and is not validated agricultural advice. Confirm irrigation "
    "decisions using actual field conditions and qualified local guidance."
    if not URDU
    else "یہ صرف تعلیمی نمونہ ہے۔ آبپاشی کا فارمولا سادہ اور غیر تصدیق شدہ "
         "ہے۔ آبپاشی کا فیصلہ حقیقی کھیت کی حالت اور مستند مقامی مشورے سے کریں۔"
)

st.markdown("""
<div class="footer">
     Zarkhez Zameen AI | Smart Farming Prototype
</div>
""", unsafe_allow_html=True)