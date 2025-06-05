import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from llm_utils import chat_with_gemini_with_context, get_recommendations
from clustering import predict_cluster
from pdf_utils import extract_text

# --- Streamlit Page Config ---
st.set_page_config(page_title="Health Risk Analyzer", page_icon="🏥", layout="wide")

# --- Header ---
st.title("🏥 Health Risk Analyzer & Chat Assistant")

# --- Upload Medical PDFs ---
st.subheader("Upload Your Medical Records (Optional)")
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
pdf_text = extract_text(uploaded_files) if uploaded_files else ""

if pdf_text:
    st.text_area("Extracted Medical Records", pdf_text, height=200)

# --- Input Form ---
st.subheader("Enter Your Health Information")
with st.form("health_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120, value=30)
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=170.0)
    systolic_bp = st.number_input("Systolic BP", min_value=0, max_value=250, value=120)
    diastolic_bp = st.number_input("Diastolic BP", min_value=0, max_value=150, value=80)
    heart_rate = st.number_input("Resting Heart Rate (bpm)", min_value=0, max_value=200, value=70)
    smoking_status = st.selectbox("Smoking Status", ["Never smoked", "Former smoker", "Current smoker"])
    exercise_days = st.slider("Exercise Days per Week", 0, 7, 3)
    cholesterol = st.selectbox("Cholesterol", ["Normal", "High", "Unknown"])
    diet = st.text_input("Briefly Describe Your Diet")
    symptoms = st.multiselect("Symptoms", ["None", "Fever", "Cough", "Fatigue", "Difficulty breathing"])
    conditions = st.multiselect("Chronic Conditions", ["None", "Diabetes", "Hypertension", "Heart disease"])
    submitted = st.form_submit_button("Analyze My Health")

# --- Analysis & Output ---
if submitted:
    bmi = round(weight / ((height / 100) ** 2), 1)
    bmi_category = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    bp_category = "Normal"
    if systolic_bp >= 140 or diastolic_bp >= 90:
        bp_category = "Hypertension Stage 2"
    elif systolic_bp >= 130 or diastolic_bp >= 80:
        bp_category = "Hypertension Stage 1"
    elif systolic_bp >= 120:
        bp_category = "Elevated"

    user_data = {
        "name": name,
        "age": age,
        "gender": gender,
        "weight_kg": weight,
        "height_cm": height,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "cholesterol": cholesterol,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "bp_category": bp_category,
        "resting_hr": heart_rate,
        "smoking_status": smoking_status,
        "exercise_days": exercise_days,
        "diet": diet,
        "symptoms": symptoms if "None" not in symptoms else [],
        "chronic_conditions": conditions if "None" not in conditions else []
    }

    df = pd.DataFrame([{
        "age": age,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "heart_rate": heart_rate,
        "smoker": 1 if smoking_status == "Current smoker" else 0,
        "exercise_frequency": exercise_days,
        "diabetes": 1 if "Diabetes" in conditions else 0,
        "hypertension": 1 if "Hypertension" in conditions else 0,
        "heart_disease": 1 if "Heart disease" in conditions else 0,
        "has_fever": 1 if "Fever" in symptoms else 0,
        "has_cough": 1 if "Cough" in symptoms else 0,
        "has_fatigue": 1 if "Fatigue" in symptoms else 0,
        "has_breathing_difficulty": 1 if "Difficulty breathing" in symptoms else 0
    }])

    cluster = predict_cluster(df)
    risk_factors = [
        f for f in [
            "Obesity" if bmi > 30 else "",
            "Underweight" if bmi < 18.5 else "", 
            "High blood pressure" if "Hypertension" in bp_category else "",
            "Smoking" if smoking_status == "Current smoker" else "",
            "Low physical activity" if exercise_days < 3 else ""
        ] + conditions + symptoms if f and f != "None"]

    st.subheader("📊 Health Summary")
    st.metric("BMI", f"{bmi} ({bmi_category})")
    st.metric("Blood Pressure", f"{systolic_bp}/{diastolic_bp} ({bp_category})")
    st.metric("Risk Level", cluster.upper())
    st.markdown(f"**Identified Risk Factors**: {', '.join(risk_factors)}")

    st.subheader("📋 AI-Powered Health Recommendations")
    recommendations = get_recommendations(user_data, cluster, risk_factors, pdf_text)
    st.markdown(recommendations)

# --- Chat Interface ---
st.markdown("---")
st.header("💬 Ask a Health Question")
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

chat_input = st.text_input("Ask about symptoms, diet, medication, etc.")
if st.button("Send") and chat_input:
    response = chat_with_gemini_with_context(chat_input, pdf_text)
    st.session_state['chat_history'].append((chat_input, response))

for q, a in st.session_state['chat_history']:
    st.markdown(f"**You:** {q}")
    st.markdown(f"**AI:** {a}")
