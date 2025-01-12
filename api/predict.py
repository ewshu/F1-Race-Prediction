from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.race_predictions import F1RacePredictor

predictor = F1RacePredictor()


def handler(request):
    if request.method == 'OPTIONS':
        # Cors preflight response
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)

    if request.method == 'POST':
        try:
            # Vercel serverless functions get data differently
            data = request.get_json()
            predictions = predictor.make_predictions(data)

            # Add CORS headers
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }

            return (jsonify(predictions), 200, headers)
        except Exception as e:
            error_response = {'error': str(e)}
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
            return (jsonify(error_response), 500, headers)