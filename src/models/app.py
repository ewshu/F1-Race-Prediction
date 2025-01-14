from flask import Flask, request, jsonify
from flask_cors import CORS
from race_predictions import F1RacePredictor

app = Flask(__name__)
# Update CORS settings to allow your Vercel domain
CORS(app, resources={
    r"/*": {
        "origins": ["https://f1-winner-prediction.vercel.app", "http://localhost:3000"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})

predictor = F1RacePredictor()

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    # Handle preflight request
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://f1-winner-prediction.vercel.app')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.json
        predictions = predictor.make_predictions(data)
        response = jsonify(predictions)
        response.headers.add('Access-Control-Allow-Origin', 'https://f1-winner-prediction.vercel.app')
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)