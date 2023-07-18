import os
import pytest
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from config import FOLDER_LIVE_DATA
from webscraping import (
    scrape_allocine_films, 
    list_to_df, 
    #df_to_csv, 
    #get_most_recent_csv
)

def test_scrape_allocine_films():
    # Test that the function returns a list
    films = scrape_allocine_films()
    assert isinstance(films, list)

    # Test that the returned list contains dictionaries
    if films:
        assert isinstance(films[0], dict)

"""def test_list_to_df():
    # Test that the function returns a DataFrame
    test_list = [{'title': 'Film 1', 'duration': '90 min'},
                  {'title': 'Film 2', 'duration': '120 min'}]
    df = list_to_df(test_list)
    assert isinstance(df, pd.DataFrame)
"""
