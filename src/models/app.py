from flask import Flask, request, jsonify
from flask_cors import CORS
from race_predictions import F1RacePredictor
import os

app = Flask(__name__)
# Replace the complex CORS setup with a simpler one
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

predictor = F1RacePredictor()

@app.route('/api/predict', methods=['POST', 'OPTIONS'])  # Added OPTIONS
def predict():
    if request.method == "OPTIONS":  # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.json
        predictions = predictor.make_predictions(data)
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)