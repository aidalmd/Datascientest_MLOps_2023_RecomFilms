import pandas as pd
from datetime import datetime
import pytz

from webscraping import scrape_allocine_films
from utils.config import URL


# TODO: decorators with the following functions

def list_to_df(List: list) -> pd.DataFrame:
    try:
        df = pd.DataFrame(List)
        print("DataFrame successfully created.")
        return df
    except Exception as e:
        print(f"Error occurred while creating the DataFrame: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

films = scrape_allocine_films(base_url=URL)
df = list_to_df(films)


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

# TODO: change types 
# TODO: EDA function

def df_to_csv(df: pd.DataFrame, folder: str, filename: str):
    try:
        tz = pytz.timezone('Europe/Paris')
        timestamp = datetime.now(tz).strftime("%Y%m%d%H%M")
        file_path = f'./{folder}/{filename}_{timestamp}.csv'
        df.to_csv(file_path, index=False)
        print("CSV file successfully created.")
    except Exception as e:
        print(f"Error occurred while creating the CSV file: {str(e)}")

films_csv = df_to_csv(df, 'data', 'scraped_films')