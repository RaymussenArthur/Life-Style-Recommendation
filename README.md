# Life-Style Recommendation API

This repository contains the machine learning backend for a lifestyle recommendation system.

The project consists of a Python-based machine learning model that is deployed as a **Flask API**. This API is designed to be consumed by a separate **Android mobile application**, which handles the user interface.

## Project Goal

The goal of this project is to recommend lifestyle choices (e.g., diet, exercise, activities) to users based on their input. The ML model provides the "brain," and the Android app provides the "face."

## Project Architecture

This system works in two parts:

1.  **Machine Learning API (This Repository):**
    * A model is trained in the Jupyter Notebooks (`Cleaning.ipynb`, `EDA.ipynb`, `Modeling.ipynb`).
    * The trained model is saved in the `/models` directory.
    * The `flask_app.py` file loads the model and exposes it as a web API. An endpoint (e.g., `/predict`) receives data from the app and returns the model's recommendation as a response.

2.  **Android App (Separate Project):**
    * A native Android app (likely built in Kotlin or Java) provides the user interface.
    * When a user requests a recommendation, the app sends an HTTP request (e.g., using Retrofit or Volley) to the running Flask API.
    * The app receives the API's response (e.g., in JSON format) and displays the recommendation to the user.

## Tech Stack

* **Machine Learning:** Python, Pandas, Scikit-learn, XGBoost (Update as needed)
* **API:** Flask
* **Data Analysis:** Jupyter Notebook

## How to Run the API

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/RaymussenArthur/Life-Style-Recommendation.git](https://github.com/RaymussenArthur/Life-Style-Recommendation.git)
    cd Life-Style-Recommendation
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask API server:**
    ```bash
    flask run
    # Or: python flask_app.py
    ```
    The API will now be running (usually at `http://127.0.0.1:5000`). The Android app can now send requests to this address.

## Android App

**Link to Android App Repo:** ` `
