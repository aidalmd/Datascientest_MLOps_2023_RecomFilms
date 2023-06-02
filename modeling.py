import functools
import pandas as pd
import numpy as np
from sklearn.metrics import PredictionErrorDisplay
import yaml
import pickle
import os
import time
import pytz
from datetime import datetime
from unidecode import unidecode
from fuzzywuzzy import process
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#nltk.download('stopwords')
import nltk
from nltk.stem.porter import PorterStemmer

from config import FOLDER_DATA
from data_management import create_table, retrieve_data_from_server


def function_timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        return result
    return wrapper

# Load the config.yaml file
with open('model/cbs_config.yaml') as file:
    cfg = yaml.safe_load(file)

# We retrieve the data from MySQL server
df = retrieve_data_from_server(db_name='recommendation', 
                           table_name='films')

def prepare_data_model(df:pd.DataFrame, cfg):
    # Drop specified columns
    columns_to_drop = [col[0] for col in cfg['model']['drop_columns']]
    df = df.drop(columns_to_drop, axis=1)
    
    # Preprocess content features
    for feature in cfg['model']['content_features']:
        try: 
            if feature == 'synopsis':
                df[feature] = df[feature].apply(lambda x: x.split())
                df[feature] = df[feature].apply(str).apply(lambda x: x.replace("\\", "")
                                                            .replace("'", "")
                                                            .replace("[", "")
                                                            .replace("]", ""))
            if feature == 'title':
                df[feature] = df[feature].apply(unidecode)

            if feature == 'rating':
                df[feature] = df[feature].apply(str)
        except Exception as e:
            print(f"Error occurred while searching for feature: {str(e)}")

    # Process additional features
    for feature in cfg['model']['processed_features']:
        df[feature] = df[feature].apply(lambda x: ','.join(map(lambda i: i.replace(' ', ''),
                                                                x.split(','))))
    
    # Combine relevant features into 'tags' column
    df['tags'] = (df['genres'] + ',' + df['directors'] 
                  + ',' + df['cast'] + ',' + df['synopsis']
    )

    # Select desired columns for the final dataframe
    dataframe = df[['title', 'tags', 'rating']]
    
    # Convert 'tags' to lowercase
    dataframe.loc[:, 'tags'] = dataframe['tags'].apply(lambda x: x.lower())
    
    # Convert 'rating' to float
    dataframe.loc[:, 'rating'] = dataframe['rating'].astype(float)
    
    # Stemming function using PorterStemmer
    ps = PorterStemmer()
    def stem(text: str):
        return [ps.stem(word) for word in text.split()]
    
    # Create a list of French stopwords
    stop_words = list(stopwords.words('french'))
    
    # Create a CountVectorizer object with specified max_features and stop_words
    cv = CountVectorizer(max_features=cfg['model']['max_features'],
                         stop_words=stop_words)
    
    # Transform 'tags' column into vectors using CountVectorizer
    vectors = cv.fit_transform(dataframe['tags']).toarray()
    
    # Calculate similarity matrix using cosine similarity on the vectors
    similarity = cosine_similarity(vectors)
    
    return similarity


def get_closest_film_title(film: str):
    film_titles = df['title'].tolist()
    suggestion = process.extractOne(film, film_titles)
    
    if suggestion:
        closest_title, score = suggestion
        if score > 70:  # Set a threshold for similarity score
            return closest_title
    return None

@function_timer
def suggest_film(film: str):
    suggestion = get_closest_film_title(film)
    if suggestion:
        user_input = input(f"Did you mean to type '{suggestion}'? (Y/N): ")
        if user_input.lower() == 'y' or user_input.strip() == '':
            return suggestion
    return None

@function_timer
def give_recommendations(df: pd.DataFrame, film: str, sim=np.array):
    film_index = df[df['title'] == film].index

    if len(film_index) == 0:
        print(f"No film found with the title '{film}'.")
        return None

    film_index = film_index[0]

    distances = sim[film_index]
    top_n = cfg['recommendation']['top_n']
    rating_threshold = cfg['recommendation']['rating_threshold']

    # Filter films based on rating threshold
    filtered_films = [(i, distance) for i, distance in enumerate(distances)
                       if df.iloc[i]['rating'] >= rating_threshold]

    # Sort films by similarity and rating from highest to lowest
    similar_films = sorted(filtered_films, reverse=True,
                           key=lambda x: (x[1], -df.iloc[x[0]]['rating']))[1:(top_n + 1)]
    
    # Get the title and rating of similar films
    similar_films = [(df.iloc[i[0]]['title'], df.iloc[i[0]]['rating']) for i in similar_films]

    # Sort top_n films by rating from highest to lowest
    similar_films = sorted(similar_films[:top_n], reverse=True,
                           key=lambda x: x[1])

    results = []
    for title, rating in similar_films:
        result = f"{title} - Rating: {rating}"
        results.append(result)

    output = '\n'.join(results)
    print(output)

    films_predictions = {
        'recom_date': datetime.now(pytz.timezone('Europe/Paris')).strftime("%Y%m%d%H%M"),
        'user_film': film,
        'recommended_films': tuple(title for title, _ in similar_films),
        'recommended_ratings': tuple(rating for _, rating in similar_films)
    }
    return films_predictions

def get_satisfaction(films_predictions: dict) -> dict:
    try:
        while True:
            satisfaction = input("Was the recommendation satisfying? (Y/N): ").strip().upper()
            if satisfaction in ('Y', 'N'):
                films_predictions['satisfaction'] = satisfaction
                break
            else:
                print("Invalid input. Please enter 'Y' or 'N'.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return films_predictions

    return films_predictions


def store_predictions_df(films_predictions: dict) -> pd.DataFrame:
    return pd.DataFrame.from_dict(films_predictions) 


def save_model(model, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    similarity = prepare_data_model(df, cfg)
    # Ensuring that the model artifact is saved before generating the recommendations.
    artifacts_folder = 'artifacts'
    os.makedirs(artifacts_folder, exist_ok=True)
    model_filepath = os.path.join(artifacts_folder, 'model_artifact.pkl')
    save_model(give_recommendations, model_filepath)

    prediction = give_recommendations(df, film='Avatar',sim=similarity)
    if prediction is not None:
        df_predictions = store_predictions_df(prediction)
        create_table(db_name='recommendation', 
                table_name='predictions', 
                df=df_predictions, 
                drop_table=False)
    else:
        print("No film recommendations available.")
    

