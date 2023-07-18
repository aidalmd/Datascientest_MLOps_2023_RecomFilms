import pandas as pd
import re
import yaml
from config import FOLDER_DATA
from webscraping import LIVE_SCRAPPED_TABLE

# The most up to date scrapped csv version is used
df = pd.read_csv(f'{FOLDER_DATA}/{LIVE_SCRAPPED_TABLE}') if LIVE_SCRAPPED_TABLE else None

# Load the config.yaml file
with open('model/cbs_config.yaml') as file:
    cfg = yaml.safe_load(file)

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

# Remove '\n', 'Avec', and 'De' using a lambda function with try-except
def remove_parasite_chars(text: str):
    try:
        text = text.replace('Avec\n', '')
        text = text.replace('De\n', '')
        text = text.replace('\n', '')
    except AttributeError:
        pass
    return text

def drop_rows_with_missing_values(df: pd.DataFrame, 
                                            content_features: list) -> pd.DataFrame:
    print('# of rows before computation: ', len(df))
    try:
        # Drop rows with missing values in content features
        df = df.dropna(subset=content_features)
        print('# of rows after computation: ', len(df))
        return df
    except Exception as e:
        print("An error occurred:", str(e))
        return None


if __name__ == "__main__":
    # Apply the duration conversion function to the 'duration' column
    df['duration_min'] = df['duration'].apply(convert_duration_to_minutes)
    df = df.drop('duration', axis=1)
    df = df.applymap(lambda x: remove_parasite_chars(x) if isinstance(x, str) 
                     else x)
    # The cleaned, transformed version of scraped_films data
    LIVE_PROCESSED_TABLE = df = drop_rows_with_missing_values(df, cfg['model']['content_features'])
    LIVE_PROCESSED_TABLE.to_csv(f'{FOLDER_DATA}/processed_films.csv', index=False)

