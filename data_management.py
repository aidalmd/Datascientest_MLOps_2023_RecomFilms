import os
from datetime import datetime
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import dotenv_values

config = dotenv_values('.env')

HOST = config['SSH_HOSTNAME']
#HOST = config['DB_HOST']
USER = config['DB_USER']
PASSWORD = config['DB_PASSWORD']

def create_database(db_name: str):
    try:
        mydb = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
        )

        mycursor = mydb.cursor()
        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print("Database created successfully.")
    except mysql.connector.Error as e:
        print("Error while creating database:", e)

def create_table(db_name: str, 
                 table_name: str, 
                 df: pd.DataFrame, 
                 drop_table: bool=False):
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            db=db_name
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print("You're connected to the database:", record)
            
            if drop_table:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                print(f"Table {table_name} already existing. Droping...")

            table_exists = False
            show_tables_query = f"SHOW TABLES LIKE '{table_name}'"
            cursor.execute(show_tables_query)
            if cursor.fetchone():
                table_exists = True

            if not table_exists:
                print('Creating table....')
                column_definitions = []
                for column_name, column_type in zip(df.columns, df.dtypes):
                    if column_type == 'float64':
                        column_definitions.append(f"`{column_name}` FLOAT(10,1)")
                    elif column_type == 'int64':
                        column_definitions.append(f"`{column_name}` INT")
                    elif column_name == 'synopsis':
                        column_definitions.append(f"`{column_name}` TEXT")
                    else:
                        column_definitions.append(f"`{column_name}` VARCHAR(255)")

                create_table_query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
                cursor.execute(create_table_query)
                print(f"Table {table_name} is created....")

            # Inserting data into the table
            placeholders = ", ".join(["%s"] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({placeholders})"
            data = df.values.tolist()
            cursor.executemany(insert_query, data)
            print(f"New row inserted in table: {table_name}.")

            # The connection is not auto-committed by default, so we must commit to save our changes
            conn.commit()
            
    except mysql.connector.Error as e:
        print("Error while connecting to MySQL:", e)

def retrieve_data_from_server(db_name: str, table_name: str) -> pd.DataFrame:
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            db=db_name
        )

        if conn.is_connected():
            cursor = conn.cursor()
            select_query = f"SELECT * FROM {table_name}"
            cursor.execute(select_query)

            # Fetch all rows from the table
            rows = cursor.fetchall()

            # Get column names
            column_names = [column[0] for column in cursor.description]

            # Create a DataFrame from the fetched rows and column names
            df = pd.DataFrame(rows, columns=column_names)
            return df
    except mysql.connector.Error as e:
        print("Error while connecting to MySQL:", e)



if __name__ == "__main__":
    # Uncomment the following line to create the 'recommendation' database
    #create_database('recommendation')
    LIVE_PROCESSED_TABLE = pd.read_csv('data/processed_films.csv')
    # Call the function to create the table and insert data
    create_table(db_name='recommendation', 
                table_name='films', 
                df=LIVE_PROCESSED_TABLE, 
                drop_table=False) # TODO: change into True
    
# TODO: create users and predictions tables