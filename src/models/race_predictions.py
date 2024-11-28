import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime


class F1RacePredictor:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.models_dir = os.path.join(project_root, 'src', 'models', 'output')

        # Load models and scalers
        try:
            self.models = {
                'Race Winner': joblib.load(os.path.join(self.models_dir, 'race winner_random_forest_model.joblib')),
                'Podium': joblib.load(os.path.join(self.models_dir, 'podium_random_forest_model.joblib')),
                'Points Finish': joblib.load(os.path.join(self.models_dir, 'points finish_random_forest_model.joblib')),
                'Top 5': joblib.load(os.path.join(self.models_dir, 'top 5_random_forest_model.joblib'))
            }

            self.scalers = {
                'Race Winner': joblib.load(os.path.join(self.models_dir, 'race winner_scaler.joblib')),
                'Podium': joblib.load(os.path.join(self.models_dir, 'podium_scaler.joblib')),
                'Points Finish': joblib.load(os.path.join(self.models_dir, 'points finish_scaler.joblib')),
                'Top 5': joblib.load(os.path.join(self.models_dir, 'top 5_scaler.joblib'))
            }

            # Load feature information
            self.feature_info = joblib.load(os.path.join(self.models_dir, 'feature_info.joblib'))
            print("Models, scalers, and feature information loaded successfully!")

        except Exception as e:
            print(f"Error loading models: {e}")
            raise

    def get_user_input(self):
        """Get race information from user"""
        print("\n=== F1 Race Prediction System ===")
        print("\nPlease enter the following information:")

        data = {}

        try:
            # Grid and Qualifying
            data['GridPosition'] = int(input("\nStarting Grid Position (1-20): "))
            data['PositionsGained'] = 0  # This will be calculated later

            # Qualifying Times
            data['Q1_seconds'] = float(input("Q1 Time in seconds (e.g., 82.5): "))
            data['Q2_seconds'] = float(input("Q2 Time in seconds (or 0 if didn't participate): "))
            data['Q3_seconds'] = float(input("Q3 Time in seconds (or 0 if didn't participate): "))

            # Best Qualifying Time
            quali_times = [t for t in [data['Q1_seconds'], data['Q2_seconds'], data['Q3_seconds']] if t > 0]
            data['BestQualiTime'] = min(quali_times) if quali_times else data['Q1_seconds']

            # Race Information
            current_year = datetime.now().year
            data['year'] = int(input(f"Year of race ({current_year}): ") or current_year)
            data['round'] = int(input("Round number of the season (1-23): "))
            data['Points'] = 0  # This will be calculated based on position
            data['laps'] = int(input("Number of laps in the race: "))

            # Encoded Categories
            print("\nConstructor codes:")
            print("0: Mercedes, 1: Red Bull, 2: Ferrari, 3: McLaren, 4: Alpine")
            print("5: AlphaTauri, 6: Aston Martin, 7: Williams, 8: Alfa Romeo, 9: Haas")
            data['Constructor_encoded'] = int(input("\nEnter constructor code (0-9): "))

            print("\nTrack codes:")
            print("Enter a number between 0-21 for different tracks")
            data['raceName_encoded'] = int(input("Enter track code (0-21): "))

            return data

        except ValueError as e:
            print(f"\nError: Please enter valid numerical values. {str(e)}")
            return None

    def make_predictions(self, input_data):
        """Make predictions using all models"""
        predictions = {}

        # Convert input to DataFrame
        input_df = pd.DataFrame([input_data])

        # Ensure columns are in the correct order
        input_df = input_df[self.feature_info['feature_columns']]

        for target, model in self.models.items():
            try:
                # Scale the input data using the corresponding scaler
                scaled_input = self.scalers[target].transform(input_df)

                # Get prediction probabilities
                prob = model.predict_proba(scaled_input)[0][1]
                predictions[target] = prob

            except Exception as e:
                print(f"Error making {target} prediction: {e}")
                predictions[target] = None

        return predictions

    def display_predictions(self, predictions):
        """Display predictions in a user-friendly format"""
        print("\n=== Race Predictions ===")

        valid_predictions = {k: v for k, v in predictions.items() if v is not None}

        if not valid_predictions:
            print("No valid predictions could be made.")
            return

        # Sort predictions by probability
        sorted_predictions = dict(sorted(valid_predictions.items(), key=lambda x: x[1], reverse=True))

        print("\nPredicted Probabilities:")
        for outcome, probability in sorted_predictions.items():
            percentage = probability * 100
            bar_length = int(percentage / 2)
            bar = '█' * bar_length + '░' * (50 - bar_length)
            print(f"\n{outcome}:")
            print(f"{bar} {percentage:.1f}%")

        # Overall interpretation
        top_outcome = max(sorted_predictions.items(), key=lambda x: x[1])
        print(f"\nBest predicted outcome: {top_outcome[0]} ({top_outcome[1] * 100:.1f}% probability)")

        if top_outcome[1] > 0.5:
            print("Strong chance of achieving this result!")
        elif top_outcome[1] > 0.3:
            print("Moderate chances of success.")
        else:
            print("This might be a challenging race.")

    def run_prediction(self):
        """Main prediction workflow"""
        while True:
            input_data = self.get_user_input()

            if input_data is None:
                retry = input("\nWould you like to try again? (yes/no): ")
                if retry.lower() not in ['y', 'yes']:
                    break
                continue

            predictions = self.make_predictions(input_data)
            self.display_predictions(predictions)

            another = input("\nWould you like to make another prediction? (yes/no): ")
            if another.lower() not in ['y', 'yes']:
                break

        print("\nThank you for using the F1 Race Predictor!")


if __name__ == "__main__":
    predictor = F1RacePredictor()
    predictor.run_prediction()