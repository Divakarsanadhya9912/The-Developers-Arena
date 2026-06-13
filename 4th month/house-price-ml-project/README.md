# 🏠 House Price Prediction System

> End-to-End Machine Learning solution for real estate price prediction using Python, scikit-learn, and Flask.

---

## 📋 Project Overview

This project builds a **production-ready ML system** that predicts house prices based on property features. It compares three algorithms, performs comprehensive evaluation, and serves predictions through a clean web interface.

**Business Problem:** Real estate agents and buyers need accurate, data-driven property valuations to make informed decisions.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/house-price-ml.git
cd house-price-ml

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset
python data/generate_data.py

# 4. Train models
python src/train.py

# 5. Launch web app
python app/web_app.py

# 6. Open browser → http://localhost:5000
```

---

## 📁 Project Structure

```
house-price-ml/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── data/
│   ├── house_prices.csv         # Dataset (300 properties)
│   ├── generate_data.py         # Data generation script
│   └── data_dictionary.md       # Column descriptions
├── src/
│   ├── data_preprocessing.py    # Cleaning, validation, feature engineering
│   ├── model_training.py        # Train & compare 3 ML algorithms
│   ├── model_inference.py       # Prediction logic with validation
│   └── train.py                 # Main training pipeline (run this)
├── models/
│   ├── *.pkl                    # Saved model files
│   ├── model_registry.json      # Model versioning metadata
│   └── training_results.json    # Metrics from last run
├── app/
│   ├── web_app.py               # Flask web application
│   ├── templates/index.html     # Web UI
│   └── static/                  # CSS and JavaScript
├── tests/
│   └── test_ml_system.py        # 24 unit tests (pytest)
├── docs/
│   └── plots/                   # Generated evaluation charts
└── config/
    └── config.yaml              # Configuration parameters
```

---

## 🛠️ Technical Requirements Met

| Requirement | Implementation |
|---|---|
| Data preprocessing pipeline | `src/data_preprocessing.py` — scaling, encoding, validation |
| 3+ ML algorithms compared | Linear Regression, Random Forest, Gradient Boosting |
| Multiple evaluation metrics | MAE, RMSE, R², MAPE, 5-fold CV |
| Feature importance | Permutation importance + tree feature importances |
| Web interface | Flask app at `app/web_app.py` |
| Model persistence | joblib serialization + version registry |
| Error handling | Input validation in `model_inference.py` |
| Modular code structure | Separate modules for each concern |

---

## 📊 Model Performance

| Model              | R²     | MAE (₹)     | MAPE  |
|--------------------|--------|-------------|-------|
| Linear Regression  | 0.9462 | ₹11,98,342  | 7.79% |
| Gradient Boosting  | 0.9416 | ₹12,45,271  | 7.85% |
| Random Forest      | 0.8649 | ₹18,35,799  | 11.63%|

✅ **Best Model:** Linear Regression (R² = 0.9462)

---

## 🔗 API Endpoints

| Method | Endpoint      | Description                 |
|--------|---------------|-----------------------------|
| GET    | `/`           | Web UI                      |
| POST   | `/predict`    | Predict from web form       |
| POST   | `/api/predict`| REST API (JSON in/out)      |
| GET    | `/api/health` | Model health check          |
| GET    | `/api/options`| Valid locations & types     |

### API Example

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"area_sqft":1200,"bedrooms":3,"bathrooms":2,"age_years":5,
       "floors":5,"parking_spaces":1,"location":"City Center","property_type":"Apartment"}'
```

Response:
```json
{
  "success": true,
  "predicted_price": 12450000,
  "lower_bound": 10831500,
  "upper_bound": 14068500,
  "formatted_price": "₹12,450,000",
  "formatted_range": "₹10,831,500 – ₹14,068,500"
}
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
# 24 tests covering preprocessing, validation, edge cases
```

---

## 🔧 Feature Engineering

6 new features are derived from raw data:
- `room_ratio` — bathrooms/bedrooms ratio
- `total_rooms` — combined room count
- `is_new` — flag for properties ≤ 5 years old
- `has_parking` — binary parking indicator
- `size_category` — Small / Medium / Large / Luxury
- `price_per_sqft` — used in EDA

---

## 📈 Top Feature Importances

1. **area_sqft** — 38% importance
2. **location** — 32% (City Center & Waterfront command premium)
3. **property_type** — 24% (Villa highest, Studio lowest)
4. **bedrooms** — 2.2%
5. **total_rooms** — 1.1%

---

## 💡 Business Insights

- Square footage and location together explain **>70%** of price variation
- City Center properties are priced ~40% higher than rural equivalents
- New properties (≤5 years) command a measurable premium
- Each additional bedroom adds approximately ₹8,00,000 on average

---

## 📦 Dependencies

```
pandas, numpy, scikit-learn, flask, joblib, matplotlib, seaborn, pytest
```

See `requirements.txt` for pinned versions.
