from fastapi import FastAPI, Security, Depends, HTTPException, status
from typing import List, Optional, Tuple
import uuid
from uuid import UUID, uuid4
import numpy as np
import pandas as pd
import mysql.connector
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.api_key import APIKeyHeader
from dotenv import dotenv_values
import yaml
from fastapi.openapi.utils import get_openapi

from modeling import (
    give_recommendations,
    prepare_data_model,
    store_predictions_df
)
from data_management import (
    create_table, 
    retrieve_data_from_server
)

# uvicorn api:app --reload

config = dotenv_values('.env')

HOST = config['SSH_HOSTNAME']
#HOST = config['DB_HOST']
USER = config['DB_USER']
PASSWORD = config['DB_PASSWORD']
API_KEY_NAME = config['API_KEY_NAME']
API_KEY = config['API_KEY']

config = {
    'user': USER,
    'password': PASSWORD,
    'host': HOST,
    'database': 'recommendation',
    'raise_on_warnings': True
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

app = FastAPI(
    title="TLWYLIGYWYN",
    description="Application de recommandation de films",
    version="0.1.0",
)

class User(BaseModel):
    id: Optional[UUID] = uuid4() 
    username: str
    password : str

class Film(BaseModel):
    title: str

class Recommendation(BaseModel):
    recom_date: str
    user_film: str
    recommended_films: Tuple[str, ...]
    recommended_ratings: Tuple[float, ...]

# Loading the users table directly from MySQL Server
db = retrieve_data_from_server(db_name='recommendation', table_name='users') 

# Load the configuration from config.yaml file
def load_config(file_path: str) -> dict:
    with open(file_path) as file:
        config = yaml.safe_load(file)
    return config

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials):
    query = f"SELECT COUNT(*) FROM users WHERE username = '{credentials.username}' AND password = '{credentials.password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result[0] == 0:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/users/me")
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    authenticate_user(credentials)
    return {"username": credentials.username, "password": credentials.password}

@app.get("/admin/protected", dependencies=[Depends(get_api_key)])
def admin_protected():
    return {"message": "Admin access granted"}

@app.get("/admin/users", dependencies=[Depends(get_api_key)])
def get_users():
 return db

@app.post("/admin/creation/users", dependencies=[Depends(get_api_key)])
def create_user(user: User):
    # Check if the username already exists
    query = f"SELECT COUNT(*) FROM users WHERE username = '{user.username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result[0] > 0:
        raise HTTPException(status_code=401, detail="Username already taken.")

    # Insert the new user into the table
    query = f"INSERT INTO users (username, password) VALUES ('{user.username}', '{user.password}')"
    cursor.execute(query)
    connection.commit()
    return {"message": "User created successfully."}


@app.delete("/admin/deletion/users/{user_id}", dependencies=[Depends(get_api_key)])
def delete_user(user_id: uuid.UUID):
    # Convert the UUID to a string
    user_id_str = str(user_id)

    # Delete the user from the table
    query = "DELETE FROM users WHERE id = %s"
    cursor.execute(query, (user_id_str,))
    connection.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}



@app.get("/api/v1/films", dependencies=[Depends(get_current_user)])
def get_films():
    # Fetch all titles of films from the table
    query = "SELECT title FROM films"
    cursor.execute(query)
    results = cursor.fetchall()
    # Extract films from the results
    films = [result[0] for result in results]
    return films

# We retrieve the table films from MySQL server
@app.get("/api/v1/table_films", dependencies=[Depends(get_current_user)])
def get_table_films():
    query = "SELECT * FROM films"
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=[column[0] for column in cursor.description])
    films_list = df.to_dict(orient='records')
    return films_list


def get_recommendations(film: Film, output=int) -> Recommendation:
    # Load the model and configuration
    with open('model/cbs_config.yaml') as file:
        cfg = yaml.safe_load(file)
    
    query = "SELECT * FROM films"
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=[column[0] for column in cursor.description])

    # Prepare the data and calculate similarity
    similarity = prepare_data_model(df, cfg)

    # Get the recommendations
    predictions = give_recommendations(df, film=film.title, sim=similarity)

    if predictions is None:
        return None
    
    # Create a Recommendation object that we'll need to store
    recommendation = Recommendation(
        recom_date=predictions['recom_date'],
        user_film=predictions['user_film'],
        recommended_films=tuple(predictions['recommended_films']),
        recommended_ratings=tuple(predictions['recommended_ratings'])
    )
    # Insert the recommendation into the pred table using parameterized query
    df_predictions = store_predictions_df(predictions)
    create_table(db_name='recommendation', 
                 table_name='predictions', 
                 df=df_predictions, 
                 drop_table=False)
    
    # Displaying the recommended films
    recommended_films = predictions['recommended_films']

    if output == 1:
        return list(recommended_films)
    elif output ==2:
        return recommendation
    
# get the title of the recommended films
@app.post("/api/v1/recommendations", response_model=List[str], 
          dependencies=[Depends(get_current_user)])
def recommend_films(film: Film):
    return get_recommendations(film, output=1)

# get the title, score of the recommended films
@app.post("/api/v1/recommendations/predictions", response_model=Recommendation, 
          dependencies=[Depends(get_current_user)])
def predictions(film: Film):
    return get_recommendations(film, output=2)

# I have to rethink the two final functions cuz both of them store scores and title