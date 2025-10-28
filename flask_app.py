import joblib
import pandas as pd
from flask import Flask, request, jsonify

# 1. INISIALISASI & LOAD MODEL
# Buat aplikasi Flask
app = Flask(__name__)

# Load model saat server pertama kali dijalankan
try:
    workout_model = joblib.load("models/workout_goal_pipeline.joblib")
    meal_model = joblib.load("models/meal_macro_pipeline.joblib")
    print("Models loaded successfully.")
except FileNotFoundError:
    print("Error: Model files not found. Make sure 'models/...' paths are correct.")
    workout_model = None
    meal_model = None

# 2. BUAT API ENDPOINT
# Endpoint root/utama
@app.route("/")
def read_root():
    # Mengirimkan status OK dalam format JSON
    return jsonify({"status": "OK", "message": "Lifestyle Prediction API is running."})


# Endpoint prediksi
@app.route("/predict", methods=["POST"])
def predict_lifestyle():
    """
    Menerima input data user (dalam format JSON) dan mengembalikan prediksi
    untuk workout dan meal.
    """
    if workout_model is None or meal_model is None:
        return jsonify({"error": "Models are not loaded. Check server logs."}), 500

    # 1. Ambil data JSON yang dikirim oleh mobile app
    input_data = request.get_json()

    # Cek jika data ada
    if not input_data:
        return jsonify({"error": "No input data provided."}), 400

    # Ganti nama key agar sesuai dengan kolom di DataFrame (Weight (kg) -> Weight_kg)
    try:
        input_data["Weight (kg)"] = input_data.pop("Weight_kg")
        input_data["Height (m)"] = input_data.pop("Height_m")
    except KeyError:
         return jsonify({"error": "Missing required fields (Weight_kg or Height_m)."}), 400
    
    # 2. Konversi input dictionary ke DataFrame
    df = pd.DataFrame([input_data])
    
    # 3. Siapkan data untuk masing-masing model
    try:
        # Data untuk Workout Model
        workout_features = ['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Experience_Level']
        workout_df = df[workout_features]
        
        # Data untuk Meal Model
        meal_features = ['Age', 'Gender', 'Weight (kg)', 'Height (m)', 
                         'diet_type', 'cooking_method', 'serving_size_g']
        meal_df = df[meal_features]

    except KeyError as e:
        return jsonify({"error": f"Missing feature in input data: {str(e)}"}), 400

    # 4. Lakukan Prediksi
    workout_prediction = workout_model.predict(workout_df)
    meal_prediction = meal_model.predict(meal_df)

    # 5. Format Output
    workout_targets = workout_prediction[0]
    meal_targets = meal_prediction[0]

    response = {
        "prediction_id": pd.Timestamp.now().strftime("%Y%m%d-%H%M%S"),
        "input_data": input_data, # Mengirim kembali data yang sudah di-adjust
        "predicted_workout_goal": {
            "target_session_duration_hours": round(workout_targets[0], 2),
            "target_calorie_burn_kcal": round(workout_targets[1], 2)
        },
        "predicted_meal_goal": {
            "target_calories_kcal": round(meal_targets[0], 2),
            "target_protein_g": round(meal_targets[1], 2),
            "target_carbs_g": round(meal_targets[2], 2),
            "target_fat_g": round(meal_targets[3], 2)
        }
    }
    
    # Mengirimkan hasil dalam format JSON
    return jsonify(response)