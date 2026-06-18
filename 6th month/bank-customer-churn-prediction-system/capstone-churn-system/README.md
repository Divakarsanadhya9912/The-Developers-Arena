# Bank Customer Churn Prediction System
 An Industry-Ready Capstone Project with End-to-End MLOps Pipeline

---

## 1. Project Overview & Business Value

### The Business Challenge
In the retail banking sector, acquiring a new customer is **5 to 25 times more expensive** than retaining an existing one. Customer churn—the rate at which loyal customers terminate their relationship with a financial institution—directly impacts a bank’s bottom-line profitability and market share. 

This repository implements a **production-ready Customer Churn Prediction System**. By leveraging machine learning models (specifically optimized **XGBoost** and **Scikit-learn** pipelines), the system predicts the probability of customer departure, categorizes high-risk cohorts, and provides business stakeholders with real-time risk scoring and visual insights via an interactive decision-support application.

### Business Value & ROI Metrics
* **Proactive Retentive Actions:** Armed with churn risk probabilities, the bank's marketing and relation teams can initiate targeted promotional campaigns (e.g., fee waivers, customized financial counseling, custom interest rate offers).
* **Quantifiable Savings:** By targeting the top 10% high-risk churn candidates with a retention success rate of 20%, an average bank can save millions in lost deposits annually.
* **Feature Importance Insights:** Identifying key churn drivers (e.g., inactive memberships, zero balances, specific geographic zones) enables the bank's product design team to optimize retention strategies at a systemic level.

---

## 2. System Architecture

The system is designed with a decoupled, modular, and cloud-native microservices architecture to ensure high availability, horizontal scalability, and strict separation of concerns.

```
                    ┌─────────────────────────┐
                    │  Customer Churn Datasets │
                    └────────────┬────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  ML Pipeline (Train)  │ ◄─── Experiment Tracking (MLflow)
                     └───────────┬───────────┘
                                 │ Generates serialized artifacts (model.pkl)
                                 ▼
                     ┌───────────────────────┐
                     │  Model Store (S3/Obj) │
                     └───────────┬───────────┘
                                 │ Loads lightweight pickle structure
                                 ▼
┌───────────────────────────────────────────────────────────────────┐
│                           DOCKER ENGINE                           │
│                                                                   │
│   ┌───────────────────────┐               ┌───────────────────┐   │
│   │   REST API Backend    │◄──────────────┤   BI Dashboard    │   │
│   │   (FastAPI / Pydantic)│  HTTP JSON    │ (Streamlit / D3)  │   │
│   └───────────────────────┘               └───────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

### Component Details
1. **ML Pipeline (`ml_pipeline/`)**: Handles modern robust feature engineering, scaling, target-encoding, checking for multi-collinearity, hyperparameter tuning, model training, and schema enforcement. It integrates with **MLflow** for rigorous lineage and run verification.
2. **API Backend (`backend/`)**: Built on high-performance **FastAPI**, wrapping the inference model in robust Pydantic data structures for sub-millisecond predictions, data schema assurance, and systematic response modeling.
3. **Frontend Dashboard (`frontend/`)**: Built on **Streamlit**, providing a direct web panel for batch inferences, bulk raw customer-csv uploads, individual "What-If" parameter tuning, and dynamic charts for management reporting.

---

## 3. Directory Layout

The workspace is organized as follows:

```text
/capstone-churn-system/
├── backend/
│   ├── main.py                # FastAPI application & endpoints
│   ├── schemas.py             # Pydantic schemas for request/response bodies
│   └── requirements.txt       # Unified Python dependencies for service hosting
├── frontend/
│   ├── app.py                 # Streamlit graphical BI panel
│   └── requirements.txt       # Streamlit dashboard libraries
├── ml_pipeline/
│   ├── train.py               # XGBoost training sequence, MLflow orchestration
│   └── preprocessor.py        # Robust pipeline for variable encoding & scaling
├── docker-compose.yml         # Containerized local environment orchestrator
├── backend.Dockerfile         # Production multi-stage Dockerfile for FastAPI
├── frontend.Dockerfile        # Production Dockerfile for Streamlit Dashboard
└── README.md                  # System Documentation and Deployment Guide
```

---

## 4. Key Data Schema & Constraints

The system is calibrated around the industrial `customer_churn.csv` dataset, which maps transactional footprint, metadata, and financial indicators to a binary churn indicator.

| Feature Name | Type | Description | Range / Validation Constraint |
|:---|:---|:---|:---|
| **CreditScore** | *Integer* | Customer's evaluated credit standing | `[300 - 850]` |
| **Geography** | *String* | Country of residence | `{'France', 'Spain', 'Germany'}` |
| **Gender** | *String* | Customer's gender identity | `{'Male', 'Female'}` |
| **Age** | *Integer* | Age of customer in years | `[18 - 100]` |
| **Tenure** | *Integer* | Years as a client | `[0 - 10]` |
| **Balance** | *Float* | Current deposit/savings aggregate | `[0.0 - 500,000.00]` |
| **NumOfProducts** | *Integer* | Active bank sub-accounts or contracts | `[1 - 4]` |
| **HasCrCard** | *Binary* | Holds active credit card | `0` (No) or `1` (Yes) |
| **IsActiveMember** | *Binary* | Frequently transacting member | `0` (No) or `1` (Yes) |
| **EstimatedSalary** | *Float* | Projected annual income | `[0.0 - 300,000.00]` |
| **Exited** *(Target)*| *Binary* | Churn status of customer | `1` (Churned) or `0` (Retained) |

---

## 5. Deployment & Execution Instructions

Ensure you have **Docker** and **Docker Compose** installed on your workstation.

### Local Deployment with Docker Compose

1. **Clone & Spin Up Containers**:
   To build and start the API backend and the Streamlit frontend concurrently in their respective networks:
   ```bash
   docker-compose up --build -d
   ```

2. **Verify Port Mappings**:
   * **FastAPI Backend (REST API)**: Running on [http://localhost:8000](http://localhost:8000) (Interactive OpenAPI documentation available at `/docs`).
   * **Streamlit BI Panel (Frontend)**: Running on [http://localhost:8501](http://localhost:8501).

3. **Check Container Statuses**:
   ```bash
   docker-compose ps
   ```

4. **Shutdown Services**:
   ```bash
   docker-compose down
   ```

---

## 6. Machine Learning Methodology

Our production pipeline is meticulously engineered to prevent information leakage, maximize evaluation validity, and streamline the paths to production:

* **Robust Data Transformations:** Categorical columns are normalized via target or one-hot encoding on the training folds ONLY, preventing training leakage. Balance and scalar features are handled via `StandardScaler`.
* **Imbalanced Target Management:** Since bank churn sets have skewed targets (typically ~20% churn vs ~80% retention), we employ `Scale_Pos_Weight` custom parameters in **XGBoost** to balance class sensitivity alongside advanced F1/ROC-AUC threshold tuning.
* **Strict Serialization:** Model schemas are exported with corresponding metadata, feature names, and specific python versions to avoid pickle unpickling runtime failures.
