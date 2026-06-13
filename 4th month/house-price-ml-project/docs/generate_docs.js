const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageBreak
} = require('docx');
const fs = require('fs');

const BLUE = "1a237e";
const LIGHT_BLUE = "D5E8F0";
const HEADER_BG = "E8EAF6";
const ACCENT = "0d47a1";
const GRAY = "718096";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 2 } },
    children: [new TextRun({ text, bold: true, color: BLUE, size: 32, font: "Arial" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 140 },
    children: [new TextRun({ text, bold: true, color: ACCENT, size: 26, font: "Arial" })]
  });
}

function h3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, color: "2d3748", size: 24, font: "Arial" })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 22, font: "Arial", ...opts })]
  });
}

function bullet(text, ref = "main-bullets") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial" })]
  });
}

function codeBlock(text) {
  return new Paragraph({
    spacing: { before: 60, after: 60 },
    shading: { fill: "F7F7F7", type: ShadingType.CLEAR },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 4 } },
    indent: { left: 360 },
    children: [new TextRun({ text, font: "Courier New", size: 18, color: "2d3748" })]
  });
}

function tableRow(cells, isHeader = false) {
  return new TableRow({
    tableHeader: isHeader,
    children: cells.map(({ text, width = 2340, color = isHeader ? HEADER_BG : "FFFFFF" }) =>
      new TableCell({
        borders,
        width: { size: width, type: WidthType.DXA },
        shading: { fill: color, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({
            text, size: 20, bold: isHeader, font: "Arial",
            color: isHeader ? BLUE : "2d3748"
          })]
        })]
      })
    )
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function separator() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "E2E8F0" } },
    children: []
  });
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "main-bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
      },
      {
        reference: "num-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
      }
    ]
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 } }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 }
      }
    },
    children: [

      // ── COVER PAGE ─────────────────────────────────────────────────────────
      new Paragraph({ spacing: { before: 2880 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        children: [new TextRun({ text: "HOUSE PRICE PREDICTION SYSTEM", bold: true, size: 44, color: BLUE, font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 240 },
        children: [new TextRun({ text: "End-to-End Machine Learning Solution", size: 28, color: ACCENT, font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        children: [new TextRun({ text: "Comprehensive Project Documentation", size: 24, color: GRAY, font: "Arial", italics: true })]
      }),
      new Paragraph({ spacing: { before: 1440 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Submitted By: [Your Name]", size: 22, font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Course: Machine Learning | Date: June 2026", size: 22, font: "Arial" })]
      }),

      pageBreak(),

      // ── SECTION 1: PROJECT OVERVIEW ─────────────────────────────────────────
      h1("1. Project Overview & Objectives"),

      h2("1.1 Business Problem Statement"),
      para("The real estate industry relies heavily on accurate property valuations for buying, selling, and investment decisions. Traditional methods are often slow, subjective, and inconsistent. This project builds an automated, data-driven House Price Prediction System that provides objective, instant property valuations backed by machine learning."),

      h2("1.2 Project Objectives"),
      bullet("Build a complete end-to-end ML pipeline from raw data to deployed web service"),
      bullet("Compare 3 different ML algorithms and select the best performer"),
      bullet("Engineer meaningful features to improve predictive accuracy"),
      bullet("Create a production-ready Flask web application for real-time predictions"),
      bullet("Implement comprehensive evaluation metrics and model interpretation"),
      bullet("Ensure robustness through input validation, error handling, and unit testing"),

      h2("1.3 Dataset Summary"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 3120, 3120],
        rows: [
          tableRow([
            { text: "Attribute", width: 3120 },
            { text: "Value", width: 3120 },
            { text: "Notes", width: 3120 }
          ], true),
          tableRow([{ text: "Total Records", width: 3120 }, { text: "300 properties", width: 3120 }, { text: "Realistic simulated data", width: 3120 }]),
          tableRow([{ text: "Features (Raw)", width: 3120 }, { text: "8 columns", width: 3120 }, { text: "Numeric + Categorical", width: 3120 }]),
          tableRow([{ text: "Engineered Features", width: 3120 }, { text: "+6 derived", width: 3120 }, { text: "From domain knowledge", width: 3120 }]),
          tableRow([{ text: "Train / Test Split", width: 3120 }, { text: "240 / 60 (80/20)", width: 3120 }, { text: "Random seed = 42", width: 3120 }]),
          tableRow([{ text: "Target Variable", width: 3120 }, { text: "Price (INR)", width: 3120 }, { text: "Continuous regression", width: 3120 }])
        ]
      }),

      separator(),
      pageBreak(),

      // ── SECTION 2: SETUP ─────────────────────────────────────────────────────
      h1("2. Setup & Installation Instructions"),

      h2("2.1 Prerequisites"),
      bullet("Python 3.10 or higher"),
      bullet("pip package manager"),
      bullet("Git (for cloning the repository)"),
      bullet("4GB RAM minimum (8GB recommended)"),

      h2("2.2 Step-by-Step Installation"),
      h3("Step 1: Clone the Repository"),
      codeBlock("git clone https://github.com/YOUR_USERNAME/house-price-ml.git"),
      codeBlock("cd house-price-ml"),

      h3("Step 2: Install Dependencies"),
      codeBlock("pip install -r requirements.txt"),

      h3("Step 3: Generate Dataset"),
      codeBlock("python data/generate_data.py"),

      h3("Step 4: Train Models"),
      codeBlock("python src/train.py"),

      h3("Step 5: Launch Web App"),
      codeBlock("python app/web_app.py"),
      codeBlock("# Open browser at: http://localhost:5000"),

      h2("2.3 Dependencies (requirements.txt)"),
      codeBlock("pandas>=2.0.0       # Data manipulation"),
      codeBlock("numpy>=1.24.0       # Numerical computing"),
      codeBlock("scikit-learn>=1.3.0 # ML algorithms & preprocessing"),
      codeBlock("flask>=3.0.0        # Web framework"),
      codeBlock("joblib>=1.3.0       # Model serialization"),
      codeBlock("matplotlib>=3.7.0   # Plotting"),
      codeBlock("seaborn>=0.12.0     # Statistical visualization"),
      codeBlock("pytest>=7.4.0       # Testing framework"),

      separator(),
      pageBreak(),

      // ── SECTION 3: CODE STRUCTURE ──────────────────────────────────────────
      h1("3. Code Structure Explanation"),

      h2("3.1 Directory Hierarchy"),
      codeBlock("house-price-ml/"),
      codeBlock("  README.md                    # Project overview & quick start"),
      codeBlock("  requirements.txt             # All Python dependencies"),
      codeBlock("  data/"),
      codeBlock("    house_prices.csv           # 300-row training dataset"),
      codeBlock("    generate_data.py           # Dataset creation script"),
      codeBlock("    data_dictionary.md         # Column descriptions"),
      codeBlock("  src/"),
      codeBlock("    data_preprocessing.py      # Load, clean, engineer features"),
      codeBlock("    model_training.py          # Train & compare 3 algorithms"),
      codeBlock("    model_inference.py         # Prediction + validation"),
      codeBlock("    train.py                   # Main training pipeline"),
      codeBlock("  app/"),
      codeBlock("    web_app.py                 # Flask web application"),
      codeBlock("    templates/index.html       # Web UI"),
      codeBlock("    static/css/style.css       # Styles"),
      codeBlock("    static/js/app.js           # Frontend JavaScript"),
      codeBlock("  models/"),
      codeBlock("    *.pkl                      # Serialized model files"),
      codeBlock("    model_registry.json        # Version tracking"),
      codeBlock("    training_results.json      # Metrics from training"),
      codeBlock("  tests/"),
      codeBlock("    test_ml_system.py          # 24 pytest unit tests"),
      codeBlock("  config/config.yaml           # Hyperparameters & paths"),
      codeBlock("  docs/plots/                  # Generated evaluation charts"),

      h2("3.2 Module Descriptions"),

      h3("data_preprocessing.py"),
      bullet("load_data(): Reads CSV with initial validation"),
      bullet("validate_data(): Drops nulls, removes invalid rows (negative prices, zero area)"),
      bullet("engineer_features(): Creates 6 derived features from domain knowledge"),
      bullet("build_preprocessor(): Returns sklearn ColumnTransformer (StandardScaler + OneHotEncoder)"),
      bullet("prepare_data(): Full pipeline returning train/test splits"),

      h3("model_training.py"),
      bullet("MODELS dict: Configures Linear Regression, Random Forest, Gradient Boosting"),
      bullet("train_all_models(): Trains each model, runs 5-fold CV, collects metrics"),
      bullet("get_best_model(): Selects winner by R² score"),
      bullet("get_feature_importance(): Extracts importance from tree models or uses permutation"),
      bullet("save_model(): Serializes pipeline with metadata and updates model registry"),

      h3("model_inference.py"),
      bullet("validate_input(): Checks all fields for ranges and valid categories"),
      bullet("prepare_input(): Replicates training feature engineering for new data"),
      bullet("predict_price(): Runs pipeline.predict() with 13% confidence band"),
      bullet("batch_predict(): Bulk prediction for lists of properties"),

      h3("web_app.py (Flask)"),
      bullet("GET / — Renders the prediction form (index.html)"),
      bullet("POST /predict — Receives form JSON, returns prediction"),
      bullet("POST /api/predict — REST API endpoint for developers"),
      bullet("GET /api/health — Model health check endpoint"),
      bullet("GET /api/options — Returns valid locations and property types"),

      separator(),
      pageBreak(),

      // ── SECTION 4: TECHNICAL REQUIREMENTS MET ─────────────────────────────
      h1("4. Technical Requirements — How Each Was Met"),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3600, 5760],
        rows: [
          tableRow([{ text: "Requirement", width: 3600 }, { text: "Implementation", width: 5760 }], true),
          tableRow([
            { text: "Data preprocessing pipeline + feature engineering", width: 3600 },
            { text: "src/data_preprocessing.py: StandardScaler, OneHotEncoder, 6 engineered features (room_ratio, size_category, is_new, has_parking, total_rooms, price_per_sqft)", width: 5760 }
          ]),
          tableRow([
            { text: "3+ ML algorithms compared", width: 3600 },
            { text: "Linear Regression (baseline), Random Forest (ensemble), Gradient Boosting (boosting) — all implemented in src/model_training.py", width: 5760 }
          ]),
          tableRow([
            { text: "Multiple evaluation metrics", width: 3600 },
            { text: "MAE, RMSE, R², MAPE, and 5-fold cross-validation score for each model", width: 5760 }
          ]),
          tableRow([
            { text: "Feature importance analysis", width: 3600 },
            { text: "Permutation importance for all models; tree feature_importances_ for RF and GB; bar chart visualization saved to docs/plots/", width: 5760 }
          ]),
          tableRow([
            { text: "Web interface for predictions", width: 3600 },
            { text: "Flask app at app/web_app.py with responsive HTML form (app/templates/index.html) and AJAX prediction", width: 5760 }
          ]),
          tableRow([
            { text: "Model persistence & versioning", width: 3600 },
            { text: "joblib serialization to models/*.pkl with timestamp; version metadata in models/model_registry.json", width: 5760 }
          ]),
          tableRow([
            { text: "Error handling & input validation", width: 3600 },
            { text: "validate_input() checks all 8 fields with specific error messages; Flask error handlers for 404/500; try/except throughout", width: 5760 }
          ]),
          tableRow([
            { text: "Production-ready modular design", width: 3600 },
            { text: "Separate modules: preprocessing, training, inference, web app. Configuration in config.yaml. Logging throughout. 24 pytest unit tests.", width: 5760 }
          ])
        ]
      }),

      separator(),
      pageBreak(),

      // ── SECTION 5: MODEL PERFORMANCE ──────────────────────────────────────
      h1("5. Model Performance Analysis"),

      h2("5.1 Comparative Results"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 1400, 1700, 1700, 1200, 1520, 1500],
        rows: [
          tableRow([
            { text: "Model", width: 2340 },
            { text: "R\u00B2 Score", width: 1400 },
            { text: "MAE (\u20B9)", width: 1700 },
            { text: "RMSE (\u20B9)", width: 1700 },
            { text: "MAPE", width: 1200 },
            { text: "CV R\u00B2", width: 1520 },
            { text: "CV Std", width: 1500 }
          ], true),
          tableRow([
            { text: "Linear Regression ✅", width: 2340, color: "E8F5E9" },
            { text: "0.9462", width: 1400, color: "E8F5E9" },
            { text: "11,98,342", width: 1700, color: "E8F5E9" },
            { text: "15,77,647", width: 1700, color: "E8F5E9" },
            { text: "7.79%", width: 1200, color: "E8F5E9" },
            { text: "0.9372", width: 1520, color: "E8F5E9" },
            { text: "±0.0108", width: 1500, color: "E8F5E9" }
          ]),
          tableRow([
            { text: "Gradient Boosting", width: 2340 },
            { text: "0.9416", width: 1400 },
            { text: "12,45,271", width: 1700 },
            { text: "16,43,411", width: 1700 },
            { text: "7.85%", width: 1200 },
            { text: "0.9091", width: 1520 },
            { text: "±0.0228", width: 1500 }
          ]),
          tableRow([
            { text: "Random Forest", width: 2340 },
            { text: "0.8649", width: 1400 },
            { text: "18,35,799", width: 1700 },
            { text: "24,99,814", width: 1700 },
            { text: "11.63%", width: 1200 },
            { text: "0.7846", width: 1520 },
            { text: "±0.0396", width: 1500 }
          ])
        ]
      }),

      h2("5.2 Best Model Selection"),
      para("Linear Regression achieved the best performance with an R\u00B2 of 0.9462, meaning the model explains 94.6% of price variation in the test set. It also had the lowest MAPE (7.79%) and most stable cross-validation score (standard deviation of only 0.0108), indicating excellent generalization."),

      h2("5.3 Feature Importance (Top 5)"),
      new Table({
        width: { size: 7200, type: WidthType.DXA },
        columnWidths: [600, 3000, 1800, 1800],
        rows: [
          tableRow([
            { text: "Rank", width: 600 },
            { text: "Feature", width: 3000 },
            { text: "Importance %", width: 1800 },
            { text: "Business Meaning", width: 1800 }
          ], true),
          tableRow([{ text: "1", width: 600 }, { text: "area_sqft", width: 3000 }, { text: "38.01%", width: 1800 }, { text: "Size is primary driver", width: 1800 }]),
          tableRow([{ text: "2", width: 600 }, { text: "location", width: 3000 }, { text: "32.42%", width: 1800 }, { text: "Neighborhood premium", width: 1800 }]),
          tableRow([{ text: "3", width: 600 }, { text: "property_type", width: 3000 }, { text: "24.49%", width: 1800 }, { text: "Villa vs Studio range", width: 1800 }]),
          tableRow([{ text: "4", width: 600 }, { text: "bedrooms", width: 3000 }, { text: "2.18%", width: 1800 }, { text: "Rooms add value", width: 1800 }]),
          tableRow([{ text: "5", width: 600 }, { text: "total_rooms", width: 3000 }, { text: "1.10%", width: 1800 }, { text: "Combined room count", width: 1800 }])
        ]
      }),

      h2("5.4 Business Insights"),
      bullet("Area, location, and property type together explain 94.9% of feature importance"),
      bullet("City Center and Waterfront properties command 35-40% price premiums over rural equivalents"),
      bullet("Villas are priced approximately 50% higher than similar-sized Apartments"),
      bullet("Properties under 5 years old receive a measurable new-build premium"),
      bullet("Average prediction error of 7.79% is competitive for a real estate valuation model"),

      separator(),
      pageBreak(),

      // ── SECTION 6: DEPLOYMENT GUIDE ────────────────────────────────────────
      h1("6. Deployment Guide"),

      h2("6.1 Local Development"),
      bullet("Clone repo, install requirements.txt, run data/generate_data.py, then src/train.py"),
      bullet("Start Flask: python app/web_app.py"),
      bullet("Access at: http://localhost:5000"),

      h2("6.2 Environment Variables"),
      codeBlock("FLASK_ENV=production"),
      codeBlock("MODEL_DIR=models/"),
      codeBlock("DATA_PATH=data/house_prices.csv"),

      h2("6.3 Production Deployment (Render / Railway)"),
      para("For cloud deployment, the project is ready for services like Render.com:"),
      bullet("Set Start Command: python app/web_app.py"),
      bullet("Set Build Command: pip install -r requirements.txt && python data/generate_data.py && python src/train.py"),
      bullet("Model files (.pkl) must persist between builds (use persistent disk or retrain on startup)"),

      h2("6.4 Retraining the Model"),
      codeBlock("# With new data:"),
      codeBlock("# 1. Replace data/house_prices.csv with updated dataset"),
      codeBlock("# 2. python src/train.py"),
      codeBlock("# 3. Restart Flask (app auto-loads latest model from registry)"),

      separator(),
      pageBreak(),

      // ── SECTION 7: API DOCUMENTATION ───────────────────────────────────────
      h1("7. API Documentation"),

      h2("7.1 REST Endpoints"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [1200, 2400, 5760],
        rows: [
          tableRow([{ text: "Method", width: 1200 }, { text: "Endpoint", width: 2400 }, { text: "Description", width: 5760 }], true),
          tableRow([{ text: "GET", width: 1200 }, { text: "/", width: 2400 }, { text: "Web prediction form (HTML)", width: 5760 }]),
          tableRow([{ text: "POST", width: 1200 }, { text: "/predict", width: 2400 }, { text: "Prediction from web UI (JSON in, JSON out)", width: 5760 }]),
          tableRow([{ text: "POST", width: 1200 }, { text: "/api/predict", width: 2400 }, { text: "REST API for programmatic access", width: 5760 }]),
          tableRow([{ text: "GET", width: 1200 }, { text: "/api/health", width: 2400 }, { text: "Model status check", width: 5760 }]),
          tableRow([{ text: "GET", width: 1200 }, { text: "/api/options", width: 2400 }, { text: "Valid locations and property types", width: 5760 }])
        ]
      }),

      h2("7.2 Request Body — POST /api/predict"),
      codeBlock("{"),
      codeBlock('  "area_sqft": 1200,       // int: 100–10000'),
      codeBlock('  "bedrooms": 3,            // int: 1–10'),
      codeBlock('  "bathrooms": 2,           // int: 1–10'),
      codeBlock('  "age_years": 5,           // int: 0–100'),
      codeBlock('  "floors": 5,              // int: 1–30'),
      codeBlock('  "parking_spaces": 1,      // int: 0–5'),
      codeBlock('  "location": "City Center",'),
      codeBlock('  "property_type": "Apartment"'),
      codeBlock("}"),

      h2("7.3 Success Response"),
      codeBlock("{"),
      codeBlock('  "success": true,'),
      codeBlock('  "predicted_price": 12450000,'),
      codeBlock('  "lower_bound": 10831500,'),
      codeBlock('  "upper_bound": 14068500,'),
      codeBlock('  "formatted_price": "₹12,450,000",'),
      codeBlock('  "formatted_range": "₹10,831,500 – ₹14,068,500"'),
      codeBlock("}"),

      h2("7.4 Error Response"),
      codeBlock("{"),
      codeBlock('  "success": false,'),
      codeBlock('  "error": "Area must be between 100 and 10,000 sqft"'),
      codeBlock("}"),

      separator(),
      pageBreak(),

      // ── SECTION 8: TESTING ─────────────────────────────────────────────────
      h1("8. Testing Evidence"),

      h2("8.1 Test Suite Summary"),
      para("24 unit tests written with pytest covering three test classes:"),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 2340, 3900],
        rows: [
          tableRow([{ text: "Test Class", width: 3120 }, { text: "Tests", width: 2340 }, { text: "Coverage", width: 3900 }], true),
          tableRow([{ text: "TestDataPreprocessing", width: 3120 }, { text: "5 tests", width: 2340 }, { text: "Validation, feature engineering, size categories", width: 3900 }]),
          tableRow([{ text: "TestInputValidation", width: 3120 }, { text: "16 tests", width: 2340 }, { text: "All fields, all locations, all property types", width: 3900 }]),
          tableRow([{ text: "TestEdgeCases", width: 3120 }, { text: "3 tests", width: 2340 }, { text: "Luxury property, studio, zero-age boundary", width: 3900 }])
        ]
      }),

      h2("8.2 Test Results"),
      codeBlock("$ python -m pytest tests/ -v"),
      codeBlock("PASSED  TestDataPreprocessing::test_validate_removes_negative_price"),
      codeBlock("PASSED  TestDataPreprocessing::test_validate_drops_na"),
      codeBlock("PASSED  TestDataPreprocessing::test_engineer_features_adds_columns"),
      codeBlock("PASSED  TestDataPreprocessing::test_is_new_flag_correct"),
      codeBlock("PASSED  TestDataPreprocessing::test_size_category_correct"),
      codeBlock("PASSED  TestInputValidation::test_valid_input_passes"),
      codeBlock("PASSED  TestInputValidation::test_invalid_area_too_small"),
      codeBlock("PASSED  TestInputValidation::test_invalid_location"),
      codeBlock("..."),
      codeBlock("24 passed in 1.13s"),

      separator(),
      pageBreak(),

      // ── SECTION 9: TROUBLESHOOTING ─────────────────────────────────────────
      h1("9. Troubleshooting Guide"),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 6240],
        rows: [
          tableRow([{ text: "Issue", width: 3120 }, { text: "Solution", width: 6240 }], true),
          tableRow([
            { text: "ModuleNotFoundError on import", width: 3120 },
            { text: "Run pip install -r requirements.txt. Check Python version (3.10+).", width: 6240 }
          ]),
          tableRow([
            { text: "Model not loaded warning on startup", width: 3120 },
            { text: "Run src/train.py before starting the web app. models/ must contain .pkl files.", width: 6240 }
          ]),
          tableRow([
            { text: "FileNotFoundError: data/house_prices.csv", width: 3120 },
            { text: "Run python data/generate_data.py to generate the dataset first.", width: 6240 }
          ]),
          tableRow([
            { text: "Port 5000 already in use", width: 3120 },
            { text: "Change port in web_app.py or kill the existing process: lsof -ti:5000 | xargs kill", width: 6240 }
          ]),
          tableRow([
            { text: "Prediction returns validation error", width: 3120 },
            { text: "Check all input fields are within valid ranges. Location and property_type must exactly match valid options.", width: 6240 }
          ]),
          tableRow([
            { text: "Sparse matrix error from sklearn", width: 3120 },
            { text: "Ensure scikit-learn >= 1.3.0 (uses sparse_output=False for OneHotEncoder).", width: 6240 }
          ]),
          tableRow([
            { text: "Tests fail to import src modules", width: 3120 },
            { text: "Run pytest from the project root directory: cd house-price-ml && python -m pytest tests/ -v", width: 6240 }
          ])
        ]
      }),

      separator(),
      pageBreak(),

      // ── SECTION 10: ANALYSIS QUESTIONS ────────────────────────────────────
      h1("10. Analysis Questions"),

      h2("Q1: Which features have the strongest predictive power?"),
      para("Area (sqft) at 38%, location at 32%, and property type at 24% are the three dominant predictors. Together they account for nearly 95% of the model's predictive weight. This aligns with real estate wisdom: location and size are the most fundamental drivers of property value."),

      h2("Q2: How does model performance vary with different algorithms?"),
      para("Linear Regression outperformed both ensemble methods in this case, achieving R²=0.9462 vs Gradient Boosting (0.9416) and Random Forest (0.8649). This suggests the underlying pricing relationships are largely linear. Tree-based models may have overfit to noise in the 300-sample dataset."),

      h2("Q3: Trade-off between model complexity and accuracy?"),
      para("This project demonstrates that simpler models can outperform complex ones on smaller datasets. Linear Regression (least complex) was most accurate here, while Random Forest (most complex, 100 trees) was least accurate. Gradient Boosting was a middle ground. Complexity should be matched to dataset size and relationship type."),

      h2("Q4: How does feature engineering improve performance?"),
      para("Feature engineering added 6 derived attributes (room_ratio, size_category, is_new, has_parking, total_rooms, price_per_sqft). While the model selected most of the base features as top predictors, the size_category buckets provided useful non-linear groupings that improve handling of area effects across the price spectrum."),

      h2("Q5: Business implications of model predictions?"),
      para("The model provides actionable pricing intelligence. With a MAPE of 7.79%, predictions are accurate enough to identify over- and under-valued properties. The 13% confidence interval provides appropriate uncertainty communication to buyers and sellers. Feature importance analysis helps agents advise clients on which renovations (bedrooms vs. bathrooms vs. parking) have the highest ROI."),

      separator(),

      // ── FOOTER ─────────────────────────────────────────────────────────────
      new Paragraph({ spacing: { before: 400, after: 0 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 2, color: "E2E8F0" } },
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "House Price Prediction System  |  ML Project Documentation  |  June 2026", size: 18, color: GRAY, font: "Arial" })]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/claude/house-price-ml/docs/ML_Project_Documentation.docx', buffer);
  console.log('Documentation created successfully!');
});
