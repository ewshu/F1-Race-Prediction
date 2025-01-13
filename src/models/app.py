import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

logger.info("Starting app initialization...")

try:
    logger.info("Current directory: %s", os.getcwd())
    logger.info("Directory contents: %s", os.listdir())

    logger.info("Attempting to import F1RacePredictor...")
    from race_predictions import F1RacePredictor

    logger.info("Initializing predictor...")
    predictor = F1RacePredictor()
    logger.info("Predictor initialized successfully!")

except Exception as e:
    logger.error("Error during initialization: %s", str(e))
    logger.error("Full error: %s", str(sys.exc_info()))
    raise


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        logger.info("Received prediction request")
        data = request.json
        logger.info("Request data: %s", data)

        predictions = predictor.make_predictions(data)
        logger.info("Generated predictions: %s", predictions)

        return jsonify(predictions)
    except Exception as e:
        logger.error("Error in predict route: %s", str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)