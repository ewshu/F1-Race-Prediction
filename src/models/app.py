from flask import Flask, request, jsonify
from flask_cors import CORS
from race_predictions import F1RacePredictor
import os

app = Flask(__name__)
# Most permissive CORS setup
CORS(app, resources={r"/*": {"origins": "*"}})

predictor = F1RacePredictor()

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    # Handle preflight
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        data = request.json
        print("Received data:", data)  # Debug log
        predictions = predictor.make_predictions(data)
        response = jsonify(predictions)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)