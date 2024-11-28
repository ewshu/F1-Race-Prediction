import pandas as pd
import numpy as np
import ast
import os


class F1DataProcessor:
    def __init__(self):
        self.data_dir = 'data/csv'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_bronze_data(self):
        """Load bronze datasets"""
        try:
            self.race_df = pd.read_csv(f"{self.data_dir}/race_bronze_df.csv")
            self.quali_df = pd.read_csv(f"{self.data_dir}/qualifying_bronze_df.csv")
            print(f"Loaded {len(self.race_df)} race results and {len(self.quali_df)} qualifying results")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def extract_driver_info(self, driver_str):
        """Extract driver information from nested string"""
        try:
            driver_dict = ast.literal_eval(driver_str)
            return {
                'driverId': driver_dict.get('driverId'),
                'driverCode': driver_dict.get('code'),
                'driverName': f"{driver_dict.get('givenName')} {driver_dict.get('familyName')}",
                'driverNumber': driver_dict.get('permanentNumber')
            }
        except:
            return {
                'driverId': None,
                'driverCode': None,
                'driverName': None,
                'driverNumber': None
            }

    def extract_constructor_info(self, constructor_str):
        """Extract constructor information from nested string"""
        try:
            constructor_dict = ast.literal_eval(constructor_str)
            return constructor_dict.get('constructorId')
        except:
            return None

    def process_qualifying_times(self, time_str):
        """Convert qualifying time string to seconds"""
        if pd.isna(time_str) or time_str == '':
            return np.nan
        try:
            # Remove any quotes and extra whitespace
            time_str = str(time_str).strip('"').strip()

            # Handle different time formats
            if ':' in time_str:
                minutes, rest = time_str.split(':')
                seconds = float(minutes) * 60 + float(rest)
            else:
                seconds = float(time_str)
            return seconds
        except:
            return np.nan

    def clean_race_data(self):
        """Clean and process race results data"""
        print("Processing race data...")

        # Extract driver and constructor information
        driver_info = []
        for driver in self.race_df['Driver']:
            driver_info.append(self.extract_driver_info(driver))
        driver_df = pd.DataFrame(driver_info)

        # Merge driver information
        self.race_df = pd.concat([self.race_df.drop('Driver', axis=1), driver_df], axis=1)

        # Extract constructor information
        self.race_df['Constructor'] = self.race_df['Constructor'].apply(self.extract_constructor_info)

        # Clean up positions and points
        self.race_df['Position'] = pd.to_numeric(self.race_df['position'], errors='coerce')
        self.race_df['GridPosition'] = pd.to_numeric(self.race_df['grid'], errors='coerce')
        self.race_df['Points'] = pd.to_numeric(self.race_df['points'], errors='coerce')

        # Calculate position changes
        self.race_df['PositionsGained'] = self.race_df['GridPosition'] - self.race_df['Position']

        print("Race data processed")

    def clean_qualifying_data(self):
        """Clean and process qualifying data"""
        print("Processing qualifying data...")

        # Extract driver and constructor information
        driver_info = []
        for driver in self.quali_df['Driver']:
            driver_info.append(self.extract_driver_info(driver))
        driver_df = pd.DataFrame(driver_info)

        # Merge driver information
        self.quali_df = pd.concat([self.quali_df.drop('Driver', axis=1), driver_df], axis=1)

        # Extract constructor information
        self.quali_df['Constructor'] = self.quali_df['Constructor'].apply(self.extract_constructor_info)

        # Process qualifying times
        for q in ['Q1', 'Q2', 'Q3']:
            if q in self.quali_df.columns:
                self.quali_df[f'{q}_seconds'] = self.quali_df[q].apply(self.process_qualifying_times)

        # Calculate best qualifying time
        quali_times = ['Q1_seconds', 'Q2_seconds', 'Q3_seconds']
        self.quali_df['BestQualiTime'] = self.quali_df[quali_times].min(axis=1)

        print("Qualifying data processed")

    def merge_data(self):
        """Merge race and qualifying data"""
        print("Merging race and qualifying data...")

        # Define merge columns
        merge_cols = ['year', 'round', 'raceName', 'driverId', 'Constructor']

        # Merge datasets
        merged_df = self.race_df.merge(
            self.quali_df[merge_cols + ['Q1_seconds', 'Q2_seconds', 'Q3_seconds', 'BestQualiTime']],
            on=merge_cols,
            how='left',
            suffixes=('_race', '_quali')
        )

        print(f"Final dataset has {len(merged_df)} rows")
        return merged_df

    def process_all(self):
        """Run all processing steps"""
        if self.load_bronze_data():
            self.clean_race_data()
            self.clean_qualifying_data()
            processed_df = self.merge_data()

            # Save processed data
            output_file = f"{self.data_dir}/f1_processed_data.csv"
            processed_df.to_csv(output_file, index=False)
            print(f"Saved processed data to {output_file}")


if __name__ == "__main__":
    processor = F1DataProcessor()
    processor.process_all()