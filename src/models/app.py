import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from race_predictions import F1RacePredictor

app = Flask(__name__)
CORS(app)

print("Starting app initialization...")  # Debug print

try:
    print("Attempting to initialize predictor...")  # Debug print
    predictor = F1RacePredictor()
    print("Predictor initialized successfully!")  # Debug print
except Exception as e:
    print(f"Error initializing predictor: {str(e)}")  # Debug print
    raise

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        print("Received request")  # Debug print
        data = request.json
        print("Request data:", data)  # Debug print
        predictions = predictor.make_predictions(data)
        print("Generated predictions:", predictions)  # Debug print
        return jsonify(predictions)
    except Exception as e:
        print(f"Error in predict route: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)