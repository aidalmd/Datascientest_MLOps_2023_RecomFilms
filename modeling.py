import pandas as pd
import yaml
import pickle
import csv
import pytz
from datetime import datetime
from unidecode import unidecode
from fuzzywuzzy import process
from utils.config import FOLDER_DATA
from file_management import LIVE_PROCESSED_TABLE
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#nltk.download('stopwords')
import nltk
from nltk.stem.porter import PorterStemmer

# Load the config.yaml file
with open('modeling/cbs_config.yaml') as file:
    cfg = yaml.safe_load(file)

# The most up to date scrapped csv version is used
df = pd.read_csv(f'{FOLDER_DATA}/{LIVE_PROCESSED_TABLE}') if LIVE_PROCESSED_TABLE else None

columns_to_drop = [col[0] for col in cfg['model']['drop_columns']]
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
    df['rating'] +
    ',' +
    df['directors'] +
    ',' +
    df['cast'] +
    ',' +
    df['synopsis']
)

dataframe = df[['title', 'tags']]
dataframe.loc[:, 'tags'] = dataframe['tags'].apply(lambda x: x.lower())



ps = PorterStemmer()

def stem(text):
    return [ps.stem(word) for word in text.split()]

dataframe['tags'].apply(stem)
stop_words = list(stopwords.words('french'))

cv = CountVectorizer(max_features=cfg['model']['max_features'],
                     stop_words=stop_words)
vectors = cv.fit_transform(dataframe['tags']).toarray()
similarity = cosine_similarity(vectors)


def get_closest_movie_title(film: str):
    movie_titles = dataframe['title'].tolist()
    suggestion = process.extractOne(film, movie_titles)
    
    if suggestion:
        closest_title, score = suggestion
        if score > 70:  # Set a threshold for similarity score
            return closest_title
    return None

def give_recommendations():
    film = input("Enter a film title: ")
    film_index = dataframe[dataframe['title'] == film].index

    # Suggests a film if the input is not in the database
    if len(film_index) == 0:
        suggestion = get_closest_movie_title(film)
        if suggestion:
            user_input = input(f"Did you mean to type '{suggestion}'? (Y/N): ")
            if user_input.lower() == 'y':
                film = suggestion
                film_index = dataframe[dataframe['title'] == film].index[0]
            else:
                print(f"No film found with the title '{film}'.")
                return
        else:
            print(f"No film found with the title '{film}'.")
            return
    else:
        film_index = film_index[0]

    distances = similarity[film_index]
    top_n = cfg['recommendation']['top_n']
    similar_films = sorted(list(enumerate(distances)),
                           reverse=True,
                           key=lambda x: x[1])[1:(top_n + 1)]

    for i in similar_films:
        print(dataframe.iloc[i[0]]['title'])

    satisfaction = input("Was the recommendation satisfying? (Y/N): ")

    # Store the artifacts, predictions, and user input
    artifacts = {
        'recom_date': datetime.now(pytz.timezone('Europe/Paris')).strftime("%Y%m%d%H%M"),
        'dataframe': LIVE_PROCESSED_TABLE,
        'user_film': film,
        'film_index': film_index,
        'recommended_films': [dataframe.iloc[i[0]]['title'] for i in similar_films],
        'satisfaction': satisfaction,
        'similarity': similarity
    }

    # Append CSV data to the file
    with open('artifacts/cbs_model_output.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=artifacts.keys())

        # If the file is empty, write the header row
        if file.tell() == 0:
            writer.writeheader()

        # Write the data row
        writer.writerow(artifacts)

    pickle.dump(dataframe,open('artifacts/film_list.pkl','wb'))
    pickle.dump(similarity,open('artifacts/similarity.pkl','wb'))

    return

give_recommendations()

