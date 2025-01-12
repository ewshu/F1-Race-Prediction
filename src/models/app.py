from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from race_predictions import F1RacePredictor
import os

app = Flask(__name__)

# Set up CORS more permissively
CORS(app)

# Additional CORS configuration
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://f1-winner-prediction.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

predictor = F1RacePredictor()

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'https://f1-winner-prediction.vercel.app')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.json
        print("Received data:", data)  # Debug print
        predictions = predictor.make_predictions(data)
        print("Generated predictions:", predictions)  # Debug print
        return jsonify(predictions)
    except Exception as e:
        print("Error:", str(e))  # Debug print
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)