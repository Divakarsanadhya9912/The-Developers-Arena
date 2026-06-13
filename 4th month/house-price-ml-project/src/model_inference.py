"""
Model Inference Module
Handles predictions with validation and confidence intervals
"""

import numpy as np
import pandas as pd
import joblib
import logging
from typing import Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VALID_LOCATIONS = ['City Center', 'Suburbs', 'Rural', 'Industrial Zone', 'Waterfront']
VALID_PROPERTY_TYPES = ['Apartment', 'Villa', 'Independent House', 'Studio']


def validate_input(data: dict) -> Tuple[bool, str]:
    """Validate user input before prediction."""
    errors = []

    area = data.get('area_sqft', 0)
    if not (100 <= float(area) <= 10000):
        errors.append("Area must be between 100 and 10,000 sqft")

    bedrooms = int(data.get('bedrooms', 0))
    if not (1 <= bedrooms <= 10):
        errors.append("Bedrooms must be between 1 and 10")

    bathrooms = int(data.get('bathrooms', 0))
    if not (1 <= bathrooms <= 10):
        errors.append("Bathrooms must be between 1 and 10")

    age = int(data.get('age_years', 0))
    if not (0 <= age <= 100):
        errors.append("Property age must be between 0 and 100 years")

    location = data.get('location', '')
    if location not in VALID_LOCATIONS:
        errors.append(f"Location must be one of: {', '.join(VALID_LOCATIONS)}")

    property_type = data.get('property_type', '')
    if property_type not in VALID_PROPERTY_TYPES:
        errors.append(f"Property type must be one of: {', '.join(VALID_PROPERTY_TYPES)}")

    if errors:
        return False, "; ".join(errors)
    return True, ""


def prepare_input(data: dict) -> pd.DataFrame:
    """Prepare user input into model-ready DataFrame."""
    area = float(data['area_sqft'])
    bedrooms = int(data['bedrooms'])
    bathrooms = int(data['bathrooms'])
    age = int(data['age_years'])
    floors = int(data.get('floors', 5))
    parking = int(data.get('parking_spaces', 1))

    # Derived features (must match training)
    room_ratio = bathrooms / bedrooms
    total_rooms = bedrooms + bathrooms
    is_new = int(age <= 5)
    has_parking = int(parking > 0)

    if area <= 800:
        size_cat = 'Small'
    elif area <= 1500:
        size_cat = 'Medium'
    elif area <= 2500:
        size_cat = 'Large'
    else:
        size_cat = 'Luxury'

    return pd.DataFrame([{
        'area_sqft': area,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'age_years': age,
        'floors': floors,
        'parking_spaces': parking,
        'room_ratio': room_ratio,
        'total_rooms': total_rooms,
        'is_new': is_new,
        'has_parking': has_parking,
        'location': data['location'],
        'property_type': data['property_type'],
        'size_category': size_cat
    }])


def predict_price(pipeline, input_data: dict) -> dict:
    """Run prediction with confidence interval."""
    is_valid, error_msg = validate_input(input_data)
    if not is_valid:
        return {'success': False, 'error': error_msg}

    try:
        X = prepare_input(input_data)
        prediction = float(pipeline.predict(X)[0])

        # Confidence interval (~15% band as practical approximation)
        lower = prediction * 0.87
        upper = prediction * 1.13

        return {
            'success': True,
            'predicted_price': round(prediction),
            'lower_bound': round(lower),
            'upper_bound': round(upper),
            'formatted_price': f"₹{prediction:,.0f}",
            'formatted_range': f"₹{lower:,.0f} – ₹{upper:,.0f}"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {'success': False, 'error': f"Prediction failed: {str(e)}"}


def batch_predict(pipeline, records: list) -> pd.DataFrame:
    """Predict prices for a list of property records."""
    results = []
    for i, record in enumerate(records):
        result = predict_price(pipeline, record)
        result['index'] = i
        results.append(result)
    return pd.DataFrame(results)


def get_business_insights(importance_df: pd.DataFrame, metrics: dict) -> list:
    """Generate business insights from model results."""
    insights = []
    top = importance_df.head(1)['feature'].values[0] if len(importance_df) > 0 else "area"
    insights.append(f"'{top}' is the strongest price predictor in the model.")
    insights.append(f"Model explains {metrics.get('r2', 0)*100:.1f}% of price variation (R²).")
    insights.append(f"Average prediction error: ₹{metrics.get('mae', 0):,.0f} (MAE).")
    insights.append("Location is a key driver — City Center and Waterfront command premium pricing.")
    insights.append("Properties ≤5 years old are flagged 'new' and priced at a premium.")
    return insights
