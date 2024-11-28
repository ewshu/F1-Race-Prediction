import pandas as pd
import requests
from datetime import datetime
import time
import os
from typing import Optional, Dict, List


class F1DataCollector:
    def __init__(self):
        self.ergast_base_url = "http://ergast.com/api/f1"
        self.default_params = {"limit": 1000}

        # Create directory for data storage
        self.data_dir = 'data/csv'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"Created directory: {self.data_dir}")

    def _make_request(self, endpoint: str) -> Dict:
        """Make request to Ergast API with built-in rate limiting"""
        url = f"{self.ergast_base_url}/{endpoint}.json"
        try:
            response = requests.get(url, params=self.default_params)
            response.raise_for_status()  # Raise exception for bad status codes
            time.sleep(0.25)  # Rate limiting
            return response.json()['MRData']
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None

    def get_race_schedule(self, year: Optional[int] = None) -> pd.DataFrame:
        """Get race schedule for a specific year or current season"""
        print(f"Getting race schedule for year: {year if year else 'current'}")
        year_str = str(year) if year else "current"
        data = self._make_request(year_str)
        if data:
            races = data['RaceTable']['Races']
            return pd.DataFrame(races)
        return pd.DataFrame()

    def get_race_results(self, year: int, round_num: Optional[int] = None) -> pd.DataFrame:
        """Get race results for a specific year/round or entire season"""
        print(f"Getting race results for year: {year}, round: {round_num if round_num else 'all'}")
        endpoint = f"{year}" if round_num is None else f"{year}/{round_num}/results"
        data = self._make_request(endpoint)
        if not data:
            return pd.DataFrame()

        races = data['RaceTable']['Races']
        results = []
        for race in races:
            race_results = race['Results']
            for result in race_results:
                result.update({
                    'year': year,
                    'round': race['round'],
                    'raceName': race['raceName'],
                    'date': race['date']
                })
                results.append(result)
        return pd.DataFrame(results)

    def get_qualifying_results(self, year: int, round_num: Optional[int] = None) -> pd.DataFrame:
        """Get qualifying results for a specific year/round or entire season"""
        print(f"Getting qualifying results for year: {year}, round: {round_num if round_num else 'all'}")
        endpoint = f"{year}/qualifying" if round_num is None else f"{year}/{round_num}/qualifying"
        data = self._make_request(endpoint)
        if not data:
            return pd.DataFrame()

        races = data['RaceTable']['Races']
        qualifying = []
        for race in races:
            quali_results = race.get('QualifyingResults', [])
            for result in quali_results:
                result.update({
                    'year': year,
                    'round': race['round'],
                    'raceName': race['raceName']
                })
                qualifying.append(result)
        return pd.DataFrame(qualifying)

    def create_bronze_dataset(self, start_year: int, end_year: int) -> None:
        """Create comprehensive bronze dataset with all relevant data"""
        print(f"\nStarting data collection from {start_year} to {end_year}")
        print("This may take several minutes due to API rate limiting...")

        race_results = []
        qualifying_results = []

        for year in range(start_year, end_year + 1):
            print(f"\nProcessing year {year}...")

            # Get race schedule for the year
            schedule = self.get_race_schedule(year)
            if schedule.empty:
                print(f"No schedule found for {year}, skipping...")
                continue

            total_rounds = len(schedule)
            print(f"Found {total_rounds} races for {year}")

            # Collect data for each round
            for round_num in range(1, total_rounds + 1):
                try:
                    # Race Results
                    race_df = self.get_race_results(year, round_num)
                    if not race_df.empty:
                        race_results.append(race_df)
                        print(f"Collected race results for round {round_num}")

                    # Qualifying Results
                    quali_df = self.get_qualifying_results(year, round_num)
                    if not quali_df.empty:
                        qualifying_results.append(quali_df)
                        print(f"Collected qualifying results for round {round_num}")

                except Exception as e:
                    print(f"Error collecting data for {year} round {round_num}: {e}")
                    continue

        print("\nCombining all collected data...")

        # Combine all data
        if race_results:
            race_df = pd.concat(race_results, ignore_index=True)
            race_file = f"{self.data_dir}/race_bronze_df.csv"
            race_df.to_csv(race_file, index=False)
            print(f"Saved race results to {race_file} ({len(race_df)} rows)")
        else:
            print("No race results collected!")

        if qualifying_results:
            quali_df = pd.concat(qualifying_results, ignore_index=True)
            quali_file = f"{self.data_dir}/qualifying_bronze_df.csv"
            quali_df.to_csv(quali_file, index=False)
            print(f"Saved qualifying results to {quali_file} ({len(quali_df)} rows)")
        else:
            print("No qualifying results collected!")


# Example usage
if __name__ == "__main__":
    collector = F1DataCollector()

    # Test current season schedule
    schedule = collector.get_race_schedule()
    print("\nCurrent Season Schedule:", len(schedule), "races")

    # Create historical dataset for last 5 years
    current_year = datetime.now().year
    start_year = current_year - 10  # Collect last 10 years of data
    print(f"\nCollecting data from {start_year} to {current_year}")
    collector.create_bronze_dataset(start_year, current_year)

    print("\nData collection complete!")