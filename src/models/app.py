from flask import Flask, request, jsonify
from flask_cors import CORS
from race_predictions import F1RacePredictor

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://f1-winner-prediction.vercel.app",
            "https://f1-winner-prediction-ga6ske9sb-ewshus-projects.vercel.app",
            "http://localhost:3000"  # Keep this for local development
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

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