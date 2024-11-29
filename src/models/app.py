import os
from datetime import datetime
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


class F1WebPredictor:
    def __init__(self):
        self.setup_paths()
        self.load_models()

    def setup_paths(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.models_dir = os.path.join(current_dir, 'output')
        print(f"Looking for models in: {self.models_dir}")

    def load_models(self):
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

            self.feature_info = joblib.load(os.path.join(self.models_dir, 'feature_info.joblib'))
            st.success("Models loaded successfully!")

        except Exception as e:
            st.error(f"Error loading models: {e}")
            st.write(f"Looking in directory: {self.models_dir}")
            st.write("Available files:",
                     os.listdir(self.models_dir) if os.path.exists(self.models_dir) else "Directory not found")
            raise

    def make_predictions(self, input_data):
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
    predictor = F1WebPredictor()

    st.title("🏎️ Formula 1 Race Prediction System")
    st.write("Enter race information to get predictions for race outcomes")

    # Create three columns for better organization
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Qualifying Performance")
        grid_position = st.number_input("Starting Grid Position", 1, 20, value=1)
        q1_time = st.number_input("Q1 Time (seconds)", 70.0, 100.0, value=80.0, step=0.001)
        q2_time = st.number_input("Q2 Time (seconds)", 0.0, 100.0, value=0.0, step=0.001)
        q3_time = st.number_input("Q3 Time (seconds)", 0.0, 100.0, value=0.0, step=0.001)

    with col2:
        st.subheader("Driver & Team Performance")
        team_season_points = st.number_input("Team's Championship Points", 0, 1000, value=0)
        team_avg_points = st.number_input("Team's Average Points per Race", 0.0, 50.0, value=0.0)
        driver_points = st.number_input("Driver's Championship Points", 0, 500, value=0)
        recent_avg_position = st.number_input("Average Position (Last 3 Races)", 1.0, 20.0, value=10.0)

    with col3:
        st.subheader("Race & Track Information")
        constructor = st.selectbox(
            "Constructor",
            options=range(10),
            format_func=lambda x: ["Mercedes", "Red Bull", "Ferrari", "McLaren", "Alpine",
                                   "AlphaTauri", "Aston Martin", "Williams", "Alfa Romeo", "Haas"][x]
        )

        track = st.selectbox(
            "Track",
            options=range(22),
            format_func=lambda x: [
                "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami",
                "Monaco", "Spain", "Canada", "Austria", "Britain", "Hungary",
                "Belgium", "Netherlands", "Italy", "Singapore", "Japan",
                "Qatar", "USA", "Mexico", "Brazil", "Vegas", "Abu Dhabi"][x]
        )

        laps = st.number_input("Number of Race Laps", 40, 80, value=50)
        race_round = st.number_input("Race Round Number", 1, 23, value=1)

    # Additional information in expandable section
    with st.expander("Track History Information"):
        track_experience = st.number_input("Previous Races at this Track", 0, 15, value=0)
        avg_track_position = st.number_input("Average Finish Position at this Track", 1.0, 20.0, value=10.0)

    input_data = {
        'GridPosition': grid_position,
        'PositionsGained': 0,
        'Q1_seconds': q1_time,
        'Q2_seconds': q2_time,
        'Q3_seconds': q3_time,
        'BestQualiTime': min([t for t in [q1_time, q2_time, q3_time] if t > 0]),
        'year': datetime.now().year,
        'round': race_round,
        'Points': driver_points,
        'laps': laps,
        'Constructor_encoded': constructor,
        'raceName_encoded': track,
        'TeamSeasonPoints': team_season_points,
        'TeamAvgPoints': team_avg_points,
        'RecentAvgPosition': recent_avg_position,
        'TrackExperience': track_experience,
        'AvgTrackPosition': avg_track_position
    }

    if st.button("Make Predictions", type="primary"):
        predictions = predictor.make_predictions(input_data)

        tab1, tab2 = st.tabs(["Predictions", "Analysis"])

        with tab1:
            st.subheader("Race Predictions")
            cols = st.columns(len(predictions))
            for col, (outcome, probability) in zip(cols, predictions.items()):
                if probability is not None:
                    with col:
                        fig = create_gauge_chart(probability, outcome)
                        st.plotly_chart(fig, use_container_width=True)

            best_outcome = max(predictions.items(), key=lambda x: x[1])
            confidence = best_outcome[1]

            st.subheader("Prediction Summary")
            if confidence > 0.5:
                st.success(f"Strong chance of {best_outcome[0]}! ({confidence * 100:.1f}% probability) 🏆")
            elif confidence > 0.3:
                st.info(f"Moderate chances of {best_outcome[0]} ({confidence * 100:.1f}% probability) 🏁")
            else:
                st.warning(f"Challenging race ahead ({confidence * 100:.1f}% probability) 💪")

        with tab2:
            if hasattr(predictor.models['Race Winner'], 'feature_importances_'):
                st.subheader("Feature Importance Analysis")
                importance = pd.DataFrame({
                    'Feature': predictor.feature_info['feature_columns'],
                    'Importance': predictor.models['Race Winner'].feature_importances_
                })
                importance = importance.sort_values('Importance', ascending=True)

                fig = px.bar(importance, x='Importance', y='Feature', orientation='h',
                             title='Feature Importance for Race Prediction')
                st.plotly_chart(fig, use_container_width=True)

                st.write("This chart shows how different factors influence the prediction.")


if __name__ == "__main__":
    main()