import pandas as pd
import re

from webscraping import df_to_csv
from utils.config import FOLDER_DATA
from data_management import LIVE_SCRAPPED_TABLE

# The most up to date scrapped csv version is used
df = pd.read_csv(f'{FOLDER_DATA}/{LIVE_SCRAPPED_TABLE}') if LIVE_SCRAPPED_TABLE else None

def convert_duration_to_minutes(duration):
    try:
        # Extract hours and minutes using regular expressions
        hours_match = re.search(r'(\d+)h', duration)
        minutes_match = re.search(r'(\d+)min', duration)
        # Convert hours and minutes to integers
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        # Calculate total duration in minutes
        total_minutes = hours * 60 + minutes
        return total_minutes
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Apply the duration conversion function to the 'duration' column
df['duration_min'] = df['duration'].apply(convert_duration_to_minutes)

# Remove '\n', 'Avec', and 'De' using a lambda function with try-except
def remove_parasite_chars(text: str):
    try:
        text = text.replace('Avec\n', '')
        text = text.replace('De\n', '')
        text = text.replace('\n', '')
    except AttributeError:
        pass
    return text

df = df.applymap(lambda x: remove_parasite_chars(x) if isinstance(x, str) else x)

def display_rows_with_missing_values(df: pd.DataFrame):
    try:
        # Create a boolean mask for rows with missing values
        mask = df.isnull().any(axis=1)
        # Filter the DataFrame using the mask
        rows_with_missing = df[mask]
        return rows_with_missing
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def drop_rows_with_excessive_missing_values(df: pd.DataFrame, max_percent: float) -> pd.DataFrame:
    try:
        percent_missing = df.isnull().mean() * 100
        if percent_missing.all() < max_percent:
            print('# of rows before computation: ', len(df))
            df.dropna(inplace=True)
            print('# of rows after computation: ', len(df))
            print("Rows with missing values dropped successfully.")
        else:
            print("Excessive missing values, no rows dropped.")
        return df
    except Exception as e:
        print(f"An error occurred: {str(e)}")

df_processed = drop_rows_with_excessive_missing_values(df, 5.0)

# Create a csv file of the processed dataframe
processed_csv = df_to_csv(df_processed, 'processed_films')