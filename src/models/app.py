import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


class F1WebPredictor:
    def __init__(self):
        self.setup_paths()
        self.load_models()

    def setup_paths(self):
        # Fixed path setup
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.models_dir = os.path.join(current_dir, 'output')
        print(f"Looking for models in: {self.models_dir}")  # Debug print

    def load_models(self):
        """Load all necessary models and data"""
        try:
            # Load models
            self.models = {
                'Race Winner': joblib.load(os.path.join(self.models_dir, 'race winner_random_forest_model.joblib')),
                'Podium': joblib.load(os.path.join(self.models_dir, 'podium_random_forest_model.joblib')),
                'Points Finish': joblib.load(os.path.join(self.models_dir, 'points finish_random_forest_model.joblib')),
                'Top 5': joblib.load(os.path.join(self.models_dir, 'top 5_random_forest_model.joblib'))
            }

            # Load scalers
            self.scalers = {
                'Race Winner': joblib.load(os.path.join(self.models_dir, 'race winner_scaler.joblib')),
                'Podium': joblib.load(os.path.join(self.models_dir, 'podium_scaler.joblib')),
                'Points Finish': joblib.load(os.path.join(self.models_dir, 'points finish_scaler.joblib')),
                'Top 5': joblib.load(os.path.join(self.models_dir, 'top 5_scaler.joblib'))
            }

            # Load feature information
            self.feature_info = joblib.load(os.path.join(self.models_dir, 'feature_info.joblib'))
            st.success("Models loaded successfully!")

        except Exception as e:
            st.error(f"Error loading models: {e}")
            st.write(f"Looking in directory: {self.models_dir}")
            st.write("Available files:",
                     os.listdir(self.models_dir) if os.path.exists(self.models_dir) else "Directory not found")
            raise

    # [Rest of the code remains the same...]
    def make_predictions(self, input_data):
        """Make predictions using all models"""
        predictions = {}
        input_df = pd.DataFrame([input_data])
        input_df = input_df[self.feature_info['feature_columns']]

        for target, model in self.models.items():
            try:
                scaled_input = self.scalers[target].transform(input_df)
                prob = model.predict_proba(scaled_input)[0][1]
                predictions[target] = prob
            except Exception as e:
                st.error(f"Error making {target} prediction: {e}")
                predictions[target] = None

        return predictions


def create_gauge_chart(probability, title):
    """Create a gauge chart for probability visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability * 100,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "lightgray"},
                {'range': [33, 66], 'color': "gray"},
                {'range': [66, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    return fig


def main():
    st.set_page_config(page_title="F1 Race Predictor", layout="wide")

    # Initialize predictor
    predictor = F1WebPredictor()

    # Header
    st.title("🏎️ Formula 1 Race Prediction System")
    st.write("Enter race information to get predictions for race outcomes")

    # Create two columns for input
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Qualifying Information")
        grid_position = st.number_input("Starting Grid Position", 1, 20, value=1)
        q1_time = st.number_input("Q1 Time (seconds)", 70.0, 100.0, value=80.0, step=0.001)
        q2_time = st.number_input("Q2 Time (seconds)", 0.0, 100.0, value=0.0, step=0.001)
        q3_time = st.number_input("Q3 Time (seconds)", 0.0, 100.0, value=0.0, step=0.001)

    with col2:
        st.subheader("Race Information")
        constructor = st.selectbox(
            "Constructor",
            options=range(10),
            format_func=lambda x: ["Mercedes", "Red Bull", "Ferrari", "McLaren", "Alpine",
                                   "AlphaTauri", "Aston Martin", "Williams", "Alfa Romeo", "Haas"][x]
        )

        track = st.selectbox(
            "Track",
            options=range(22),
            format_func=lambda x: f"Track {x}"  # You can replace with actual track names
        )

        laps = st.number_input("Number of Laps", 40, 80, value=50)

    # Create input data
    input_data = {
        'GridPosition': grid_position,
        'PositionsGained': 0,
        'Q1_seconds': q1_time,
        'Q2_seconds': q2_time,
        'Q3_seconds': q3_time,
        'BestQualiTime': min([t for t in [q1_time, q2_time, q3_time] if t > 0]),
        'year': datetime.now().year,
        'round': 1,  # You can make this dynamic
        'Points': 0,
        'laps': laps,
        'Constructor_encoded': constructor,
        'raceName_encoded': track
    }

    # Make predictions when button is clicked
    if st.button("Make Predictions"):
        predictions = predictor.make_predictions(input_data)

        st.subheader("Race Predictions")

        # Create gauge charts in a grid
        cols = st.columns(len(predictions))
        for col, (outcome, probability) in zip(cols, predictions.items()):
            if probability is not None:
                with col:
                    fig = create_gauge_chart(probability, outcome)
                    st.plotly_chart(fig, use_container_width=True)

        # Add interpretation
        st.subheader("Interpretation")
        best_outcome = max(predictions.items(), key=lambda x: x[1])
        st.write(f"Best predicted outcome: **{best_outcome[0]}** "
                 f"({best_outcome[1] * 100:.1f}% probability)")

        # Add visual confidence indicator
        confidence = best_outcome[1]
        if confidence > 0.5:
            st.success("Strong chance of achieving this result! 🏆")
        elif confidence > 0.3:
            st.info("Moderate chances of success 🏁")
        else:
            st.warning("This might be a challenging race 💪")

        # Show feature importance if available
        if hasattr(predictor.models['Race Winner'], 'feature_importances_'):
            st.subheader("Feature Importance")
            importance = pd.DataFrame({
                'Feature': predictor.feature_info['feature_columns'],
                'Importance': predictor.models['Race Winner'].feature_importances_
            })
            importance = importance.sort_values('Importance', ascending=True)

            fig = px.bar(importance, x='Importance', y='Feature', orientation='h',
                         title='Feature Importance for Race Prediction')
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()