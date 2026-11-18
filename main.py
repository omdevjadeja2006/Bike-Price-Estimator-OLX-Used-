from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os

app = FastAPI(
    title="Motorcycle Valuation API",
    description="This API allows you to predict the value of a motorcycle based on its features.",
    version="1.0.0"
)

MODEL_PATH = "xgboost_bike_price_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file '{MODEL_PATH}' not found. Please ensure the model is trained and saved.")

pipeline = joblib.load(MODEL_PATH)
MAPE = 0.2124 # mean % error

try:
    preprocessor = pipeline.named_steps['preprocessing']
    target_encoder = preprocessor.named_transformers_['target_encode']

    # Match exact feature column order: ['City', 'Model', 'Brand']
    CATEGORIES = {
        "cities": sorted([str(c) for c in target_encoder.categories_[0]]),
        "models": sorted([str(c) for c in target_encoder.categories_[1]]),
        "brands": sorted([str(c) for c in target_encoder.categories_[2]])
    }
except Exception as e:
    print(f"Error extracting categories: {e}")
    CATEGORIES = {"brands": [], "models": [], "cities": []}

@app.get("/")
def home():
    return {"status": "online", "message": "Motorcycle Price Prediction API is running."}


@app.get("/categories")
def get_categories():
    """Returns unique Brands, Models, and Cities directly from model memory."""
    return CATEGORIES


class BikeInput(BaseModel):
    Brand: str = Field(..., example="Royal Enfield")
    Model: str = Field(..., example="Classic 350")
    City: str = Field(..., example="Ahmedabad")
    Year: int = Field(..., ge=1990, le=2026, example=2020)
    Age: int = Field(..., ge=0, example=6)
    KM_Driven: float = Field(..., ge=0, example=25000.0)
    KM_driven_per_year: float = Field(..., ge=0, example=4166.6)
    Is_Premium_Brand: int = Field(..., ge=0, le=1, example=1)


@app.post("/predict")
def predict_price(data: BikeInput):
    try:
        input_df = pd.DataFrame([data.model_dump()])

        # Primary point estimate prediction
        raw_prediction = float(pipeline.predict(input_df)[0])

        # Compute lower and upper negotiation bounds
        low_bound = raw_prediction * (1.0 - MAPE)
        high_bound = raw_prediction * (1.0 + MAPE)

        return {
            "exact_price": round(raw_prediction, -2),   # Rounded to nearest ₹100
            "range_low": round(low_bound, -2),
            "range_high": round(high_bound, -2),
            "mape_used": MAPE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))