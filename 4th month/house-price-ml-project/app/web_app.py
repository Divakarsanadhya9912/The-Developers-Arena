"""
Flask Web Application - House Price Prediction System
Run: python app/web_app.py
"""

import os
import sys
import json
import glob
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask, render_template, request, jsonify
from model_inference import predict_price, VALID_LOCATIONS, VALID_PROPERTY_TYPES
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load best model at startup
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
pipeline = None
model_metadata = {}


def load_latest_model():
    global pipeline, model_metadata
    registry_path = os.path.join(MODEL_DIR, 'model_registry.json')
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            registry = json.load(f)
        if registry:
            latest = registry[-1]
            data = joblib.load(os.path.join(MODEL_DIR, os.path.basename(latest['file'])))
            pipeline = data['pipeline']
            model_metadata = data['metadata']
            logger.info(f"Loaded model: {latest['model_name']}")
            return True
    # Fallback: find any .pkl
    pkls = glob.glob(os.path.join(MODEL_DIR, '*.pkl'))
    if pkls:
        data = joblib.load(sorted(pkls)[-1])
        pipeline = data['pipeline']
        model_metadata = data.get('metadata', {})
        return True
    return False


@app.route('/')
def index():
    return render_template('index.html',
                           locations=VALID_LOCATIONS,
                           property_types=VALID_PROPERTY_TYPES,
                           model_info=model_metadata)


@app.route('/predict', methods=['POST'])
def predict():
    if pipeline is None:
        return jsonify({'success': False, 'error': 'Model not loaded. Run training first.'})

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No input data provided.'})

    result = predict_price(pipeline, data)
    return jsonify(result)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """REST API endpoint for programmatic access."""
    if pipeline is None:
        return jsonify({'success': False, 'error': 'Model not loaded.'}), 503

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'JSON body required.'}), 400

    result = predict_price(pipeline, data)
    status = 200 if result['success'] else 422
    return jsonify(result), status


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': pipeline is not None,
        'model_name': model_metadata.get('model_name', 'unknown'),
        'model_version': model_metadata.get('version', 'unknown')
    })


@app.route('/api/options', methods=['GET'])
def options():
    return jsonify({
        'locations': VALID_LOCATIONS,
        'property_types': VALID_PROPERTY_TYPES
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    if load_latest_model():
        logger.info("✅ Model loaded successfully")
    else:
        logger.warning("⚠️  No model found. Run src/train.py first.")

    app.run(debug=True, host='0.0.0.0', port=5000)
