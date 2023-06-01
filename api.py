from fastapi import FastAPI, Security, Depends, HTTPException, status
from typing import List, Optional
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

from data_management import retrieve_data_from_server


config = dotenv_values('.env')

HOST = config['DB_HOST']
USER = config['DB_USER']
PASSWORD = config['DB_PASSWORD']

config = {
    'user': USER,
    'password': PASSWORD,
    'host': HOST,
    'database': 'recommendation',
    'raise_on_warnings': True
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

# uvicorn api:api --reload
# http://localhost:8000/docs#/default

api = FastAPI(
    title="TLWYLIGYWYN",
    description="Application de recommandation de films",
    version="0.1.0",
)

class User(BaseModel):
    id: Optional[UUID] = uuid4() 
    username: str
    password : str

# Define the input models
class FilmInput(BaseModel):
    film: str

class SatisfactionInput(BaseModel):
    satisfaction: str

class PredictionOutput(BaseModel):
    recom_date: str
    user_film: str
    recommended_films: List[str]
    recommended_ratings: List[float]
    satisfaction: Optional[str]


# Loading the users table directly from MySQL Server
db = retrieve_data_from_server(db_name='recommendation', table_name='users') 

@api.get("/api/v1/users")
def get_users():
 return db

@api.post("/api/v1/users")
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


@api.delete("/api/v1/users/{user_id}")
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


security = HTTPBasic()

@api.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    print(f" Received credentials: {credentials}")
    return {"username": credentials.username, "password": credentials.password}


# admin
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


@api.get("/api/v1/films")
def get_films():
    # Fetch all titles of films from the table
    query = "SELECT title FROM films"
    cursor.execute(query)
    results = cursor.fetchall()
    # Extract films from the results
    films = [result[0] for result in results]
    return films


# Load the configuration from config.yaml file
def load_config(file_path: str) -> dict:
    with open(file_path) as file:
        config = yaml.safe_load(file)
    return config

# We retrieve the films from MySQL server
@api.get("/api/v1/table_films")
def get_table_films():
    query = "SELECT * FROM films"
    cursor.execute(query)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=[column[0] for column in cursor.description])
    films_list = df.to_dict(orient='records')
    return films_list

# TODO:  add predictions in the api