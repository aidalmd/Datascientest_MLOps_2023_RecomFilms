import requests
import bs4


from requests import get
from bs4 import BeautifulSoup 
from warnings import warn
from time import sleep
from random import randint
import numpy as np, pandas as pd
import numpy as np

from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import linear_kernel



pages = np.arange(1, 12, 1)
title  = []
note = []
resume = []

for page in pages : 
    #print(page)
    def get_page_contents(page):
        page = requests.get('https://www.allocine.fr/film/meilleurs/' 
                        + '?page=' + str(page) , headers={"Accept-Language": "fr"})
        return bs4.BeautifulSoup(page.text, "html.parser")

    soup = get_page_contents(page)
    movies = soup.findAll('div', class_='card entity-card entity-card-list cf')
    titles = [movie.find('a').text for movie in movies]
    title = title + titles
    note = note +  [movie.find('span', 'stareval-note', text_attribute=False).text.strip() for movie in movies]
    resume  = resume +  [movie.find('div', 'content-txt', text_attribute=False).text.strip() for movie in movies]




films_dict = {'title': title, 'resume': resume, 'note': note }

films = pd.DataFrame(films_dict)

sw = list(fr_stop)
tfidf = TfidfVectorizer(stop_words=sw)
films['resume'] = films['resume'].fillna('')
tfidf_matrix = tfidf.fit_transform(films['resume'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

indices = pd.Series(films.index, index=films['title']).drop_duplicates()


def get_recommendations(title, cosine_sim=cosine_sim):
    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:6]

    movie_indices = [i[0] for i in sim_scores]

    return films['title'].iloc[movie_indices]



get_recommendations("Vol au-dessus d'un nid de coucou")



