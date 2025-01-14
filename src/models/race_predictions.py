import pandas as pd
import numpy as np
import joblib
import os
import logging
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class F1RacePredictor:
    def __init__(self):
        logger.info("Initializing F1RacePredictor")
        self.setup_paths()
        self.load_models()

    def setup_paths(self):
        """Set up paths for model files"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.models_dir = os.path.join(current_dir, 'output')
            logger.info(f"Models directory: {self.models_dir}")

            if os.path.exists(self.models_dir):
                logger.info(f"Models directory contents: {os.listdir(self.models_dir)}")
            else:
                raise FileNotFoundError(f"Models directory not found: {self.models_dir}")

        except Exception as e:
            logger.error(f"Error in setup_paths: {str(e)}")
            raise

    def load_models(self):
        """Load all necessary models and scalers with enhanced error handling"""
        try:
            model_files = {
                'Race Winner': 'race winner_random_forest_model.joblib',
                'Podium': 'podium_random_forest_model.joblib',
                'Points Finish': 'points finish_random_forest_model.joblib',
                'Top 5': 'top 5_random_forest_model.joblib'
            }

            scaler_files = {
                'Race Winner': 'race winner_scaler.joblib',
                'Podium': 'podium_scaler.joblib',
                'Points Finish': 'points finish_scaler.joblib',
                'Top 5': 'top 5_scaler.joblib'
            }

            # Explicitly import numpy to ensure compatibility
            import numpy

            # Load models
            self.models = {}
            for name, filename in model_files.items():
                path = os.path.join(self.models_dir, filename)
                logger.info(f"Attempting to load model: {path}")
                try:
                    # Use a more robust loading method
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        model = joblib.load(path)
                    self.models[name] = model
                    logger.info(f"Successfully loaded {name} model")
                except Exception as e:
                    logger.error(f"Error loading {name} model: {e}")
                    raise

            # Load scalers
            self.scalers = {}
            for name, filename in scaler_files.items():
                path = os.path.join(self.models_dir, filename)
                logger.info(f"Attempting to load scaler: {path}")
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        scaler = joblib.load(path)
                    self.scalers[name] = scaler
                    logger.info(f"Successfully loaded {name} scaler")
                except Exception as e:
                    logger.error(f"Error loading {name} scaler: {e}")
                    raise

            # Load feature information
            feature_info_path = os.path.join(self.models_dir, 'feature_info.joblib')
            if not os.path.exists(feature_info_path):
                raise FileNotFoundError(f"Feature info file not found: {feature_info_path}")

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.feature_info = joblib.load(feature_info_path)
                logger.info("Feature info loaded successfully!")
            except Exception as e:
                logger.error(f"Error loading feature info: {e}")
                raise

            logger.info("All models and scalers loaded successfully!")

        except Exception as e:
            logger.error(f"Critical error in load_models: {e}")
            raise
    def validate_input(self, input_data):
        """Validate input data format and values"""
        required_fields = [
            'GridPosition', 'Q1_seconds', 'Q2_seconds', 'Q3_seconds',
            'year', 'round', 'laps', 'Constructor_encoded', 'raceName_encoded',
            'Points', 'TeamSeasonPoints', 'TeamAvgPoints', 'RecentAvgPosition'
        ]

        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in input_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Validate value ranges
        if not (1 <= input_data['GridPosition'] <= 20):
            raise ValueError("Grid position must be between 1 and 20")

        if not (0 <= input_data['Constructor_encoded'] <= 9):
            raise ValueError("Constructor code must be between 0 and 9")

        if not (0 <= input_data['raceName_encoded'] <= 21):
            raise ValueError("Track code must be between 0 and 21")

        return True

    def make_predictions(self, input_data):
        """Make predictions using all models"""
        try:
            # Validate input
            self.validate_input(input_data)

            # Add BestQualiTime if not present
            if 'BestQualiTime' not in input_data:
                quali_times = [input_data[f'Q{i}_seconds'] for i in range(1, 4) if input_data[f'Q{i}_seconds'] > 0]
                input_data['BestQualiTime'] = min(quali_times) if quali_times else input_data['Q1_seconds']

            # Convert input to DataFrame
            input_df = pd.DataFrame([input_data])

            # Ensure columns are in correct order
            input_df = input_df[self.feature_info['feature_columns']]

            logger.info(f"Input data processed: {input_df.to_dict('records')[0]}")

            predictions = {}
            for target, model in self.models.items():
                try:
                    # Scale input data
                    scaled_input = self.scalers[target].transform(input_df)

                    # Get prediction probability
                    prob = model.predict_proba(scaled_input)[0][1]
                    predictions[target] = float(prob)  # Convert to float for JSON serialization

                except Exception as e:
                    logger.error(f"Error predicting {target}: {str(e)}")
                    predictions[target] = None

            logger.info(f"Generated predictions: {predictions}")
            return predictions

        except Exception as e:
            logger.error(f"Error in make_predictions: {str(e)}")
            raise


if __name__ == "__main__":
    predictor = F1RacePredictor()