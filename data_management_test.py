import pytest
import mysql.connector
import pandas as pd
from unittest import mock
from dotenv import dotenv_values
from data_management import create_database, create_table, retrieve_data_from_server

config = dotenv_values('.env')

HOST = config['DB_HOST']
USER = config['DB_USER']
PASSWORD = config['DB_PASSWORD']


# Mocking the mysql.connector.connect method
@mock.patch('mysql.connector.connect')
def test_create_database(mock_connect):
    # Mocking the cursor and its methods
    mock_cursor = mock_connect.return_value.cursor.return_value

    # Test case parameters
    db_name = 'mydb'

    # Call the function
    create_database(db_name)

    # Assertions
    mock_connect.assert_called_once_with(
        host=HOST,
        user=USER,
        password=PASSWORD
    )  # Check if mysql.connector.connect was called with the correct arguments
    mock_cursor.execute.assert_called_once_with(f"CREATE DATABASE IF NOT EXISTS {db_name}")  # Check if cursor.execute was called with the correct query
    assert mock_cursor.execute.call_count == 1  # Check if cursor.execute was called only once

class MockCursor:
    def __init__(self):
        pass
    def execute(self, query):
        pass
    def executemany(self, query, data):
        pass
    def fetchone(self):
        pass
    def close(self):
        pass

class MockConnection:
    def __init__(self):
        pass
    def cursor(self):
        return MockCursor()
    def close(self):
        pass
    def commit(self):
        pass

# Unit test for ingestion of data
def test_create_table():
    # Mocking the necessary parameters
    db_name = 'test_database'
    table_name = 'test_table'
    drop_table = False
    host = HOST
    user = USER
    password = PASSWORD

    # Mocking the database connection
    mysql.connector.connect.side_effect = MockConnection

    # Mocking the DataFrame
    df = pd.DataFrame({'column1': [1, 2, 3], 'column2': [0.1, 0.2, 0.3]})

    # Calling the create_table function
    create_table(db_name, table_name, df, drop_table)

    
# Mocking the mysql.connector.connect method
@mock.patch('mysql.connector.connect')
def test_retrieve_data_from_server(mock_connect):
    # Mocking the cursor and its methods
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [(1, 'John'), (2, 'Jane')]
    mock_cursor.description = [('id',), ('name',)]

    # Mocking the pandas DataFrame constructor
    pd.DataFrame = mock.MagicMock()

    # Test case parameters
    db_name = 'mydb'
    table_name = 'mytable'

    # Call the function
    result = retrieve_data_from_server(db_name, table_name)

    # Assertions
    assert result.equals(pd.DataFrame.return_value)  # Check if the returned DataFrame is correct
    mock_connect.assert_called_once_with(
        host=HOST,
        user=USER,
        password=PASSWORD,
        db=db_name
    )  # Check if mysql.connector.connect was called with the correct arguments
    mock_cursor.execute.assert_called_once_with(f"SELECT * FROM {table_name}")  # Check if cursor.execute was called with the correct query

# run pytest, 3 passed

