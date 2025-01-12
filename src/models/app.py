# models/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from race_predictions import F1RacePredictor

app = Flask(__name__)
CORS(app)

predictor = F1RacePredictor()

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received data:", data)  # Added debug print
        predictions = predictor.make_predictions(data)
        print("Generated predictions:", predictions)  # Added debug print
        return jsonify(predictions)
    except Exception as e:
        print("Error:", str(e))  # Added debug print
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)