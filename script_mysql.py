import mysql.connector as mysql
from mysql.connector import Error
import pandas as pd

path = r".\processed_films_202305171705.csv"

df = pd.read_csv(path, delimiter=",", index_col=0)

print(df.head(2))

df = df.drop(["duration"], axis=1)

print(df.head(2))

def create_database():
    import mysql.connector

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin1234"
    )

    mycursor = mydb.cursor()

    mycursor.execute("CREATE DATABASE recommendation")

#create_database()

def create_table():
    try:
        conn = mysql.connect(host='localhost', database='recommendation', user='root', password='admin1234')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
            cursor.execute('DROP TABLE IF EXISTS films;')
            print('Creating table....')
    # in the below line please pass the create table statement which you want #to create
            cursor.execute("CREATE TABLE films(title varchar(255),genres varchar(255), directors varchar(255), cast varchar(255), synopsis TEXT,rating FLOAT, duration_min INT)")
            print("Table is created....")
            #loop through the data frame
            for i,row in df.iterrows():
                #here %S means string values
                sql = "INSERT INTO recommendation.films VALUES (%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, tuple(row))
                print("Record inserted")
                # the connection is not auto committed by default, so we must commit to save our changes
                conn.commit()
    except Error as e:
                print("Error while connecting to MySQL", e)


create_table()
