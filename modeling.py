import pandas as pd
import numpy as np
from sklearn.metrics import PredictionErrorDisplay
import yaml
import pickle
import csv
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
from data_management import LIVE_PROCESSED_TABLE, create_table, retrieve_data_from_server


def execution_time(function):
    def function_timer(*args, **kwargs):
        start = time.time()
        res = function(*args, **kwargs)
        end = time.time()
        timer = end - start
        print('Running time for the function {}'.format(function.__name__), 'is: {} s'.format(timer))
        return res
    return function_timer


# Load the config.yaml file
with open('model/cbs_config.yaml') as file:
    cfg = yaml.safe_load(file)

# We retrieve the data from MySQL server
df = retrieve_data_from_server(db_name='recommendation', 
                           table_name='films')



columns_to_drop = [col[0] for col in cfg['model']['drop_columns']]
# we have: title,genres,directors,cast,synopsis,rating
df = df.drop(columns_to_drop, axis=1)

# Apply lambda function to each feature specified in config.yaml
for feature in cfg['model']['content_features']:
    try: 
        if feature == 'synopsis':
            df[feature] = df[feature].apply(lambda x:x.split())
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

for feature in cfg['model']['processed_features']:
    df[feature] = df[feature].apply(lambda x: ','.join(map(lambda i: i.replace(' ', ''),
                                                            x.split(','))))
    
df['tags'] = (
    df['genres'] +
    ',' +
    df['directors'] +
    ',' +
    df['cast'] +
    ',' +
    df['synopsis']
)


dataframe = df[['title', 'tags', 'rating']]
dataframe.loc[:, 'tags'] = dataframe['tags'].apply(lambda x: x.lower())
dataframe.loc[:, 'rating'] = dataframe['rating'].astype(float)



# Importing the PorterStemmer from NLTK library
ps = PorterStemmer()

# Function to perform stemming on a given text
def stem(text: str):
    # Split the text into individual words and apply stemming to each word
    return [ps.stem(word) for word in text.split()]

dataframe['tags'].apply(stem)

# Creating a list of French stopwords
stop_words = list(stopwords.words('french'))

# Creating a CountVectorizer object with specified max_features and stop_words
cv = CountVectorizer(max_features=cfg['model']['max_features'],
                     stop_words=stop_words)

# Transforming the 'tags' column of the dataframe into vectors using CountVectorizer
vectors = cv.fit_transform(dataframe['tags']).toarray()

# Calculating the similarity matrix using cosine similarity on the vectors
similarity = cosine_similarity(vectors)


def get_closest_film_title(film: str):
    film_titles = dataframe['title'].tolist()
    suggestion = process.extractOne(film, film_titles)
    
    if suggestion:
        closest_title, score = suggestion
        if score > 70:  # Set a threshold for similarity score
            return closest_title
    return None

@execution_time
def suggest_film(film: str):
    suggestion = get_closest_film_title(film)
    if suggestion:
        user_input = input(f"Did you mean to type '{suggestion}'? (Y/N): ")
        if user_input.lower() == 'y' or user_input.strip() == '':
            return suggestion
    return None

@execution_time
def give_recommendations() -> dict:
    film = input("Enter a film title: ")
    film_index = dataframe[dataframe['title'] == film].index

    if len(film_index) == 0:
        suggestion = suggest_film(film)
        if suggestion:
            film = suggestion
            film_index = dataframe[dataframe['title'] == film].index[0]
        else:
            print(f"No film found with the title '{film}'.")
            return None
    else:
        film_index = film_index[0]

    distances = similarity[film_index]
    top_n = cfg['recommendation']['top_n']
    rating_threshold = cfg['recommendation']['rating_threshold']

    # Filter films based on rating threshold
    filtered_films = [(i, distance) for i, distance in enumerate(distances)
                       if dataframe.iloc[i]['rating'] >= rating_threshold]

    # Sort films by similarity and rating from highest to lowest
    similar_films = sorted(filtered_films, reverse=True,
                           key=lambda x: (x[1], -dataframe.iloc[x[0]]['rating']))[1:(top_n + 1)]
    
    # Get the title and rating of similar films
    similar_films = [(dataframe.iloc[i[0]]['title'], dataframe.iloc[i[0]]['rating']) for i in similar_films]

    # Sort top_n films by rating from highest to lowest
    similar_films = sorted(similar_films[:top_n], reverse=True,
                           key=lambda x: x[1])

    for title, rating in similar_films:
        print(f"{title} - Rating: {rating}")

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


def store_prediction_pickle(dataframe: pd.DataFrame, similarity: np.array):
    pickle.dump(dataframe, open('artifacts/film_list.pkl', 'wb'))
    pickle.dump(similarity, open('artifacts/similarity.pkl', 'wb'))

# Call the functions
prediction = give_recommendations()

if prediction is not None:
    prediction = get_satisfaction(prediction)
    df_predictions = store_predictions_df(prediction)
    # TODO: populate the SQL Table
    create_table(db_name='recommendation', 
             table_name='predictions', 
             df=df_predictions, 
             drop_table=False)
    store_prediction_pickle(dataframe, similarity)
else:
    print("No film recommendations available.")

