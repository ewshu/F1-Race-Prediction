import os
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
        predictions = predictor.make_predictions(data)
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)