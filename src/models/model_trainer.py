import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_curve, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib

class F1ModelTrainer:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.data_dir = os.path.join(project_root, 'src', 'data_collection', 'data', 'csv')
        self.output_dir = os.path.join(project_root, 'src', 'models', 'output')
        self.random_state = 42

        # Create subdirectories for different types of plots
        self.plot_dirs = {
            'confusion_matrices': os.path.join(self.output_dir, 'confusion_matrices'),
            'feature_importance': os.path.join(self.output_dir, 'feature_importance'),
            'performance_curves': os.path.join(self.output_dir, 'performance_curves'),
            'distribution_plots': os.path.join(self.output_dir, 'distribution_plots')
        }

        for dir_path in self.plot_dirs.values():
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def load_and_clean_data(self):
        # Load data
        data_path = f"{self.data_dir}/f1_processed_data.csv"
        df = pd.read_csv(data_path)
        print(f"Initially loaded {len(df)} rows")

        # Define all features we want to use
        selected_features = [
            # Grid and Race Position Features
            'GridPosition',
            'Position',
            'PositionsGained',

            # Qualifying Performance
            'Q1_seconds',
            'Q2_seconds',
            'Q3_seconds',
            'BestQualiTime',
            'QualifyingPosition',

            # Historical Performance
            'RecentAvgPosition',
            'AvgTrackPosition',
            'TrackExperience',

            # Team Performance
            'TeamSeasonPoints',
            'TeamAvgPoints',

            # Race Information
            'Constructor',
            'raceName',
            'year',
            'round',

            # Additional Race Data
            'Points',
            'Status',
            'laps'
        ]

        # Keep only columns that exist in the dataset
        existing_features = [col for col in selected_features if col in df.columns]
        df = df[existing_features]
        print(f"\nUsing {len(existing_features)} features:")
        print(existing_features)

        # Remove rows with any missing values
        df_cleaned = df.dropna()
        print(f"\nRows after removing missing values: {len(df_cleaned)}")

        # Encode categorical variables
        le = LabelEncoder()
        categorical_columns = ['Constructor', 'raceName', 'Status']
        for col in categorical_columns:
            if col in df_cleaned.columns:
                print(f"Encoding {col}")
                df_cleaned[f'{col}_encoded'] = le.fit_transform(df_cleaned[col])

        return df_cleaned

    def create_prediction_targets(self, df):
        """Create various prediction targets from the data"""
        return {
            'Race Winner': (df['Position'] == 1).astype(int),
            'Podium': (df['Position'] <= 3).astype(int),
            'Points Finish': (df['Position'] <= 10).astype(int),
            'Top 5': (df['Position'] <= 5).astype(int),
            'Top Qualifier': (df['GridPosition'] <= 3).astype(int),
            'Position Improvement': (df['PositionsGained'] > 0).astype(int),
            'Strong Result': ((df['Position'] <= 5) & (df['GridPosition'] > 5)).astype(int)
        }

    def plot_confusion_matrix(self, y_true, y_pred, model_name, target_name):
        plt.figure(figsize=(10, 8))
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['No', 'Yes'], yticklabels=['No', 'Yes'])
        plt.title(f'{model_name} Confusion Matrix\n{target_name} Prediction')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig(os.path.join(self.plot_dirs['confusion_matrices'],
                                 f'{model_name.lower()}_{target_name.lower()}_confusion_matrix.png'))
        plt.close()

    def plot_feature_importance(self, model, feature_columns, target_name):
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': feature_columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=True)  # Changed to ascending=True for horizontal plot

            plt.figure(figsize=(12, max(8, len(feature_columns) * 0.3)))
            sns.barplot(data=importance_df, x='importance', y='feature')
            plt.title(f'Feature Importance for {target_name} Prediction')
            plt.xlabel('Importance Score')
            plt.ylabel('Features')
            plt.tight_layout()
            plt.savefig(os.path.join(self.plot_dirs['feature_importance'],
                                     f'feature_importance_{target_name.lower()}.png'))
            plt.close()

            return importance_df

    def plot_roc_curve(self, y_test, y_pred_proba, model_name, target_name):
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 8))
        plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {model_name}\n{target_name} Prediction')
        plt.legend(loc="lower right")
        plt.savefig(os.path.join(self.plot_dirs['performance_curves'],
                                 f'{model_name.lower()}_{target_name.lower()}_roc_curve.png'))
        plt.close()

    def plot_precision_recall_curve(self, y_test, y_pred_proba, model_name, target_name):
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)

        plt.figure(figsize=(8, 8))
        plt.plot(recall, precision)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - {model_name}\n{target_name} Prediction')
        plt.savefig(os.path.join(self.plot_dirs['performance_curves'],
                                 f'{model_name.lower()}_{target_name.lower()}_pr_curve.png'))
        plt.close()

    def plot_feature_distributions(self, X, y, feature_columns, target_name):
        plt.figure(figsize=(15, 10))
        num_features = min(5, len(feature_columns))  # Plot top 5 features
        for i, feature in enumerate(feature_columns[:num_features], 1):
            plt.subplot(2, 3, i)
            sns.kdeplot(data=pd.DataFrame({'feature': X[feature], 'target': y}),
                        x='feature', hue='target', common_norm=False)
            plt.title(f'{feature} Distribution by {target_name}')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dirs['distribution_plots'],
                                 f'feature_distributions_{target_name.lower()}.png'))
        plt.close()

    def train_models(self):
        # Load and prepare data
        df = self.load_and_clean_data()
        targets = self.create_prediction_targets(df)

        # Prepare features
        categorical_encoded = [col for col in df.columns if col.endswith('_encoded')]
        numeric_features = [col for col in df.columns
                            if col not in ['Position']
                            and not pd.api.types.is_string_dtype(df[col])
                            and not col.endswith('_encoded')]
        feature_columns = numeric_features + categorical_encoded
        X = df[feature_columns]

        # Save feature columns for prediction
        feature_info = {
            'feature_columns': feature_columns,
            'categorical_encoded': categorical_encoded,
            'numeric_features': numeric_features
        }
        joblib.dump(feature_info, os.path.join(self.output_dir, 'feature_info.joblib'))
        # Initialize models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10,
                                                    min_samples_split=5, random_state=self.random_state),
            'Hist Gradient Boosting': HistGradientBoostingClassifier(max_iter=100, learning_rate=0.1,
                                                                     max_depth=5, random_state=self.random_state)
        }

        # Store results for comparison
        results = []

        # Train and evaluate models for each target
        for target_name, y in targets.items():
            print(f"\nTraining models for {target_name} prediction...")

            # Split and scale data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                                random_state=self.random_state)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Plot feature distributions
            self.plot_feature_distributions(X, y, feature_columns, target_name)

            for model_name, model in models.items():
                print(f"Training {model_name}...")

                # Train model
                model.fit(X_train_scaled, y_train)

                # Save the model and scaler
                model_filename = os.path.join(self.output_dir,
                                              f'{target_name.lower()}_{model_name.lower().replace(" ", "_")}_model.joblib')
                scaler_filename = os.path.join(self.output_dir,
                                               f'{target_name.lower()}_scaler.joblib')

                joblib.dump(model, model_filename)
                joblib.dump(scaler, scaler_filename)
                print(f"Saved {model_name} and scaler for {target_name}")
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)

                # Store results
                results.append({
                    'Target': target_name,
                    'Model': model_name,
                    'Accuracy': accuracy
                })

                # Generate plots
                self.plot_confusion_matrix(y_test, y_pred, model_name, target_name)
                self.plot_roc_curve(y_test, y_pred_proba, model_name, target_name)
                self.plot_precision_recall_curve(y_test, y_pred_proba, model_name, target_name)

                if model_name == 'Random Forest':
                    importance_df = self.plot_feature_importance(model, feature_columns, target_name)
                    importance_df.to_csv(os.path.join(self.plot_dirs['feature_importance'],
                                                      f'feature_importance_{target_name.lower()}.csv'),
                                         index=False)

        # Save overall results
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(self.output_dir, 'model_results.csv'), index=False)

        # Plot overall results comparison
        plt.figure(figsize=(12, 6))
        sns.barplot(data=results_df, x='Target', y='Accuracy', hue='Model')
        plt.xticks(rotation=45)
        plt.title('Model Performance Comparison Across Targets')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'overall_model_comparison.png'))
        plt.close()


if __name__ == "__main__":
    trainer = F1ModelTrainer()
    trainer.train_models()