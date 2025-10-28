import uvicorn
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# -----------------------------------------------------------------
# 1. INISIALISASI & LOAD MODEL
# -----------------------------------------------------------------

# Buat aplikasi FastAPI
app = FastAPI(title="Lifestyle API", description="API untuk prediksi Workout dan Meal Macro")

# Load model saat server pertama kali dijalankan
# Ini memastikan model hanya di-load sekali, bukan setiap ada request
try:
    workout_model = joblib.load("models/workout_goal_pipeline.joblib")
    meal_model = joblib.load("models/meal_macro_pipeline.joblib")
    print("Models loaded successfully.")
except FileNotFoundError:
    print("Error: Model files not found. Make sure 'models/...' paths are correct.")
    workout_model = None
    meal_model = None

# -----------------------------------------------------------------
# 2. DEFINISIKAN BENTUK INPUT (PENTING)
# -----------------------------------------------------------------
# Ini memberi tahu API data apa yang akan dikirim oleh mobile app
# Ini akan memvalidasi data secara otomatis
class UserInput(BaseModel):
    Age: int
    Gender: str
    Weight_kg: float
    Height_m: float
    Experience_Level: int  # 1=Beginner, 2=Intermediate, 3=Advanced
    diet_type: str
    cooking_method: str
    serving_size_g: float
    
    # Contoh data yang bisa Anda gunakan untuk testing di API docs
    class Config:
        schema_extra = {
            "example": {
                "Age": 29,
                "Gender": "Male",
                "Weight_kg": 85.0,
                "Height_m": 1.75,
                "Experience_Level": 2,
                "diet_type": "Vegan",
                "cooking_method": "Grilled",
                "serving_size_g": 300.0
            }
        }

# -----------------------------------------------------------------
# 3. BUAT API ENDPOINT
# -----------------------------------------------------------------

# Buat endpoint root/utama
@app.get("/")
def read_root():
    return {"status": "OK", "message": "Lifestyle Prediction API is running."}


# Buat endpoint prediksi
@app.post("/predict")
def predict_lifestyle(user_input: UserInput):
    """
    Menerima input data user dan mengembalikan prediksi
    untuk workout dan meal.
    """
    if workout_model is None or meal_model is None:
        return {"error": "Models are not loaded. Check server logs."}

    # 1. Konversi input Pydantic ke dictionary lalu ke DataFrame
    # Ini penting, karena model kita dilatih menggunakan DataFrame
    input_data = user_input.dict()
    
    # Ganti nama key agar sesuai dengan kolom di DataFrame (Weight (kg) -> Weight_kg)
    # Ini karena Python/JSON tidak suka spasi atau kurung di nama variabel
    input_data["Weight (kg)"] = input_data.pop("Weight_kg")
    input_data["Height (m)"] = input_data.pop("Height_m")
    
    df = pd.DataFrame([input_data])

    # 2. Siapkan data untuk masing-masing model
    # (Sama seperti di predict.py)
    
    # Data untuk Workout Model
    workout_features = ['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Experience_Level']
    workout_df = df[workout_features]
    
    # Data untuk Meal Model
    meal_features = ['Age', 'Gender', 'Weight (kg)', 'Height (m)', 
                     'diet_type', 'cooking_method', 'serving_size_g']
    meal_df = df[meal_features]

    # 3. Lakukan Prediksi
    workout_prediction = workout_model.predict(workout_df)
    meal_prediction = meal_model.predict(meal_df)

    # 4. Format Output
    workout_targets = workout_prediction[0]
    meal_targets = meal_prediction[0]

    response = {
        "prediction_id": pd.Timestamp.now().strftime("%Y%m%d-%H%M%S"),
        "input_data": user_input.dict(),
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
    
    return response

# -----------------------------------------------------------------
# 4. (OPSIONAL) UNTUK TESTING DI KOMPUTER LOKAL
# -----------------------------------------------------------------
# Perintah ini akan menjalankan server di komputer Anda
# Buka terminal dan jalankan: python main.py
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)