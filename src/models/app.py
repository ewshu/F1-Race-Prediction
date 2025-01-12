from flask import Flask, request, jsonify
from flask_cors import CORS
from race_predictions import F1RacePredictor
import os

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://f1-winner-prediction.vercel.app"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})

predictor = F1RacePredictor()

@app.route('/api/predict', methods=['POST'])
def predict():
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