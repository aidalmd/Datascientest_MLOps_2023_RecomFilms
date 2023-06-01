import requests
import os
import pandas as pd
import pytz
from datetime import datetime
from bs4 import BeautifulSoup as bs

from config import URL, FOLDER_LIVE_DATA

def scrape_allocine_films(base_url=URL) -> list:
    """
    Scrapes film details from the Allociné website.
    Returns a list of dictionaries containing the film information.
    """

    # Initialize the list
    films = []
    # Send a GET request to the page
    response = requests.get(base_url)
    soup = bs(response.content, 'html.parser')

    # Find the number of pages
    pagination = soup.find('div', class_='pagination-item-holder').find_all('a')
    total_pages = int(pagination[-1].text)


    for page in range(1, total_pages + 1):

      # Create the URL for each page
      url = f'{base_url}?page={page}'
      response = requests.get(url)
      soup = bs(response.content, 'html.parser')

      # Find all the film items on the page
      film_items = soup.find_all('li', class_='mdl')


      for film_item in film_items:
          # Extract the film details
          title = film_item.find('h2', class_='meta-title').text.strip()

          duration_elem =  duration = film_item.find('div', class_='meta-body-item meta-body-info')
          duration_with_genres = duration_elem.text.strip() if duration_elem is not None else ''
          duration_parts = duration_with_genres.split('/', maxsplit=1)
          duration = duration_parts[0].strip() if duration_parts else ''
          
          genres = duration_parts[1].strip() if len(duration_parts) > 1 else ''

          director_elem = film_item.find('div', class_='meta-body-item meta-body-direction')
          director = director_elem.text.strip() if director_elem is not None else ''

          cast_elem = film_item.find('div', class_='meta-body-item meta-body-actor')
          cast = cast_elem.text.strip() if cast_elem is not None else ''

          synopsis = film_item.find('div', class_='synopsis').text.strip()

          rating_elem = film_item.find('span', class_='stareval-note')
          rating = rating_elem.text.strip().replace(',', '.') if rating_elem is not None else ''    

          # Create a dictionary for the film
          film = {
              'title': title,
              'duration': duration,
              'genres': genres,
              'directors': director,
              'cast': cast,
              'synopsis': synopsis,
              'rating': rating
          }

          # Add the film to the list
          films.append(film)

    return films


def list_to_df(List: list) -> pd.DataFrame:
    try:
        df = pd.DataFrame(List)
        print("1. DataFrame successfully created.")
        return df
    except Exception as e:
        print(f"Error occurred while creating the DataFrame: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

def df_to_csv(df: pd.DataFrame, filename: str):
    try:
        timestamp = datetime.now(pytz.timezone('Europe/Paris')).strftime("%Y%m%d%H%M")
        file_path = f'{FOLDER_LIVE_DATA}/{filename}_{timestamp}.csv'
        df.to_csv(file_path, index=False)
        print("2. CSV file successfully created.")
    except Exception as e:
        print(f"Error occurred while creating the CSV file: {str(e)}")


def get_most_recent_csv(folder_path, prefix):
    try:
        files = []
        # Get a list of all CSV files in the folder
        for file in os.listdir(folder_path):
            if file.startswith(prefix) and file.endswith(".csv"):
                    files.append(file)

        # Sort the scraped CSV files based on the timestamp in their names
        files.sort(key=lambda x: datetime.strptime(x.split("_")[2].split(".")[0], "%Y%m%d%H%M"))
        # Get the most recent scraped CSV file
        most_recent_file = str(files[-1]) if files else None
        # Return the names of the most recent CSV files for both categories as strings
        return most_recent_file
    except (OSError, IOError) as e:
        print("Error occurred while accessing the folder:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None


if __name__ == "__main__":
    # Executed only when the module is run directly
    films = scrape_allocine_films(base_url=URL)
    df = list_to_df(films)
    # Creating a Dataframe of the scraped data e.g.: scrapped_films_YYYYMMHHMM.csv
    df_to_csv(df, 'scrapped_films')
    # The most up to date scrapped csv version
    
LIVE_SCRAPPED_TABLE = get_most_recent_csv(folder_path=f'{FOLDER_LIVE_DATA}', prefix="scrapped")
