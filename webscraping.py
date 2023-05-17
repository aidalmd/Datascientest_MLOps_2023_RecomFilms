import requests
import pandas as pd
import pytz
from datetime import datetime
from bs4 import BeautifulSoup as bs

from utils.config import URL, FOLDER_LIVE_DATA

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
          rank_elem = film_item.find('div', class_='label-ranking')
          rank = rank_elem.text.strip() if rank_elem is not None else ''

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
              'rank': rank,
              'title': title,
              'duration': duration,
              'genres': genres,
              'director': director,
              'cast': cast,
              'synopsis': synopsis,
              'rating': rating
          }

          # Add the film to the list
          films.append(film)

    return films

films = scrape_allocine_films(base_url=URL)

def list_to_df(List: list) -> pd.DataFrame:
    try:
        df = pd.DataFrame(List)
        print("DataFrame successfully created.")
        return df
    except Exception as e:
        print(f"Error occurred while creating the DataFrame: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

df = list_to_df(films)

def df_to_csv(df: pd.DataFrame, filename: str):
    try:
        timestamp = datetime.now(pytz.timezone('Europe/Paris')).strftime("%Y%m%d%H%M")
        file_path = f'{FOLDER_LIVE_DATA}/{filename}_{timestamp}.csv'
        df.to_csv(file_path, index=False)
        print("CSV file successfully created.")
    except Exception as e:
        print(f"Error occurred while creating the CSV file: {str(e)}")

df_to_csv(df,'scrapped_films')