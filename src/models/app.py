import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from models.race_predictions import F1RacePredictor

app = Flask(__name__)
CORS(app)

predictor = F1RacePredictor()
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received data:", data)  # Add this line to log the received data
        predictions = predictor.make_predictions(data)
        print("Predictions:", predictions)  # Add this line to log the predictions
        return jsonify(predictions)
    except Exception as e:
        print("Error:", str(e))  # Add this line to log any errors
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)