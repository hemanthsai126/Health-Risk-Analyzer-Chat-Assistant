"""Rule-based risk score model to classify users into health risk clusters."""
import pandas as pd

def predict_cluster(df_row: pd.DataFrame) -> str:
    """Predicts risk level based on rule-based scoring.

    Args:
        df_row: Single-row DataFrame with health features

    Returns:
        Risk level as a string: 'very low', 'low', 'moderate', 'high', or 'very high'
    """
    bmi = df_row['bmi'].iloc[0]
    systolic_bp = df_row['systolic_bp'].iloc[0]
    diastolic_bp = df_row['diastolic_bp'].iloc[0]
    heart_rate = df_row['heart_rate'].iloc[0]
    smoker = df_row['smoker'].iloc[0]
    exercise_frequency = df_row['exercise_frequency'].iloc[0]
    diabetes = df_row['diabetes'].iloc[0]
    hypertension = df_row['hypertension'].iloc[0]
    heart_disease = df_row['heart_disease'].iloc[0]
    has_fever = df_row['has_fever'].iloc[0]
    has_cough = df_row['has_cough'].iloc[0]
    has_fatigue = df_row['has_fatigue'].iloc[0]
    has_breathing_difficulty = df_row['has_breathing_difficulty'].iloc[0]

    # Basic rule-based scoring system
    score = 0
    if bmi < 18.5 or bmi > 30:
        score += 1
    if systolic_bp > 140 or diastolic_bp > 90:
        score += 1
    if heart_rate > 100:
        score += 1
    if smoker:
        score += 1
    if exercise_frequency < 3:
        score += 1
    if diabetes:
        score += 1
    if hypertension:
        score += 1
    if heart_disease:
        score += 1
    if has_fever or has_cough or has_fatigue or has_breathing_difficulty:
        score += 1

    # Translate score into cluster
    if score == 0:
        return "very low"
    elif score <= 2:
        return "low"
    elif score <= 4:
        return "moderate"
    elif score <= 6:
        return "high"
    else:
        return "very high"
