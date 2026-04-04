import streamlit as st
import numpy as np
import pickle
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SkyFare ✈️",
    page_icon="✈️",
    layout="wide"
)

# ---------------- PAGE THEME ----------------
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
    color: white;
}

.stApp {
    background: linear-gradient(135deg, #000000, #1a0000, #330000);
}

/* Title */
.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #ff1a1a;
}

/* Card */
.card {
    background: rgba(20, 0, 0, 0.85);
    padding: 15px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(255, 0, 0, 0.2);
    margin-bottom: 17px;
    color: white;
}

/* Predict Button */
.predict-btn button {
    width: 100%;
    background-color: #ff0000;
    color: white;
    font-size: 18px;
    border-radius: 12px;
    padding: 12px;
    transition: 0.3s;
    border: none;
}

.predict-btn button:hover {
    background-color: #ff4d4d;
    transform: scale(1.03);
    color: black;
}

/* Result Box */
.result-box {
    padding: 20px;
    border-radius: 15px;
    background-color: #1a0000;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: #ff3333;
    border: 1px solid #ff0000;
}

/* Divider */
hr {
    border: 1px solid #ff1a1a;
}

</style>
""", unsafe_allow_html=True)
# ---------------- CONSTANTS ----------------
AIRLINES = ["IndiGo", "Air India", "Jet Airways", "SpiceJet", "Vistara", "GoAir"]
SOURCES = ["Delhi", "Kolkata", "Mumbai", "Chennai"]
DESTINATIONS = ["Cochin", "Delhi", "New Delhi", "Hyderabad", "Kolkata"]
TOTAL_STOPS_OPTIONS = ["Non-stop", "1 stop", "2 stops", "3 stops"]

TOTAL_STOPS_MAP = {
    "Non-stop": 0,
    "1 stop": 1,
    "2 stops": 2,
    "3 stops": 3
}

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    model_path = os.path.join("models", "rd_random.pkl")
    with open(model_path, "rb") as f:
        return pickle.load(f)

model = load_model()

# ---------------- TITLE ----------------
st.markdown('<div class="main-title">✈️ SkyFare Predictor</div>', unsafe_allow_html=True)
st.write("Smart ML-based flight fare estimation system")

st.divider()

# ---------------- INPUT CARD ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📝 Enter Flight Details")

col1, col2, col3 = st.columns(3)

with col1:
    airline = st.selectbox("Airline", AIRLINES)
    source = st.selectbox("Source", SOURCES)

with col2:
    destination = st.selectbox("Destination", DESTINATIONS)
    stops_label = st.selectbox("Total Stops", TOTAL_STOPS_OPTIONS)

with col3:
    journey_date = st.date_input("Journey Date")
    dep_time = st.time_input("Departure Time")
    arr_time = st.time_input("Arrival Time")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- AUTO DURATION ----------------
dep_total = dep_time.hour * 60 + dep_time.minute
arr_total = arr_time.hour * 60 + arr_time.minute

if arr_total < dep_total:
    arr_total += 24 * 60

duration = arr_total - dep_total
duration_hours = duration // 60
duration_minutes = duration % 60

st.info(f"🕒 Flight Duration: {duration_hours}h {duration_minutes}m")

# ---------------- FEATURE BUILD ----------------
def build_features():
    return np.array([[
        AIRLINES.index(airline),
        SOURCES.index(source),
        DESTINATIONS.index(destination),
        TOTAL_STOPS_MAP[stops_label],
        journey_date.day,
        journey_date.month,
        dep_time.hour,
        dep_time.minute,
        arr_time.hour,
        arr_time.minute,
        duration_hours,
        duration_minutes,
        0, 0, 0, 0
    ]])

# ---------------- PREDICT BUTTON ----------------
st.markdown('<div class="predict-btn">', unsafe_allow_html=True)
predict = st.button("💰 Predict Fare")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RESULT ----------------
if predict:
    try:
        X = build_features()
        prediction = model.predict(X)[0]

        st.markdown(f'<div class="result-box">Estimated Fare: ₹ {int(prediction):,}</div>', unsafe_allow_html=True)

        # Dynamic Fare Indicator
        if prediction < 4000:
            st.success("🟢 Budget Friendly Fare")
            st.progress(30)
        elif prediction < 8000:
            st.warning("🟡 Moderate Fare")
            st.progress(65)
        else:
            st.error("🔴 Expensive Fare")
            st.progress(90)

    except Exception as e:
        st.error("Prediction failed.")
        st.code(str(e))