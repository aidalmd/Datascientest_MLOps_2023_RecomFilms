import requests
import bs4
from requests import get
from bs4 import BeautifulSoup 
from warnings import warn
from time import sleep
from random import randint
import numpy as np, pandas as pd
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


from fastapi import FastAPI , Depends , Query
from typing import List, Optional 
from uuid import UUID, uuid4
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
#from typing import Annotated
from enum import Enum, auto , Flag
from fastapi import Security, Depends, FastAPI, HTTPException, status
from fastapi.security.api_key import APIKeyHeader, APIKey


api = FastAPI(
    title='Recommandation des films'
)

class User(BaseModel):
    id: Optional[UUID] = uuid4() 
    first_name: str
    password : str

db: List[User] = [
 User(
 id=uuid4(),
 first_name="hajar",
 password = "toto",
 ),
 User(
 id=uuid4(),
 first_name="toto",
 password = "hajar",
  ),
  ] 

@api.get("/api/v1/users")
def get_users():
 return db

@api.post("/api/v1/users")
def create_user(user: User):
 db.append(user)
 return {"id": user.id}

security = HTTPBasic()


@api.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    print(f" Received credentials: {credentials}")
    return {"username": credentials.username, "password": credentials.password}


## admin
API_KEY = "movies1"
API_KEY_NAME = "admin"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )







def get_page_contents(page):
    page = requests.get('https://www.allocine.fr/film/meilleurs/' 
                + '?page=' + str(page) , headers={"Accept-Language": "fr"})
    return bs4.BeautifulSoup(page.text, "html.parser")


def get_movies() : 
    pages = np.arange(1, 10, 1)
    title  = []
    note = []
    synopsis = []
    for page in pages : 
        soup = get_page_contents(page)
        movies = soup.findAll('div', class_='card entity-card entity-card-list cf')
        if movies is not None :
           titles = [movie.find('a').text for movie in movies]
           title = title + titles
           note = note +  [movie.find('span', 'stareval-note', text_attribute=False).text.strip() for movie in movies]
           synopsis  = synopsis +  [movie.find('div', 'content-txt', text_attribute=False).text.strip() for movie in movies]

    
    movies_dict = {'title': title, 'synopsis': synopsis, 'note': note }
    
    movies = pd.DataFrame(movies_dict)    
    
    return movies

@api.get('/get-data')
def get_data():
    movies = get_movies()
    return movies


sw = list(fr_stop)
tfidf = TfidfVectorizer(stop_words=sw)
movies = get_movies()
movies['synopsis'] = movies['synopsis'].fillna('')
tfidf_matrix = tfidf.fit_transform(movies['synopsis'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
def get_recommendations(title):
    
    indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()
    
    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:6]

    movie_indices = [i[0] for i in sim_scores]
    #result = movies[['title','note']].iloc[movie_indices]
    result = movies[['title','note']].sort_values(by='note', ascending = True)

    return result.iloc[movie_indices]
   




class Title(BaseModel):
    
    title: str
    
  
  
@api.post("/api/v1/recommendations")
def create_movie(user : Title):
 #db.append(user)
 #get_recommendations(movie)
 return get_recommendations(user.title)
  