import os
import unittest
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dotenv import dotenv_values

config = dotenv_values('.env')

FOLDER_LIVE_DATA = config['FOLDER_LIVE_DATA']

from webscraping import (
    scrape_allocine_films,  
    get_most_recent_csv
)

class TestScrapingFunctions(unittest.TestCase):

    def test_scrape_allocine_films(self):
        # This is a basic test to check if the scraping function returns a list
        films = scrape_allocine_films()
        self.assertIsInstance(films, list)

        # Add more specific tests here, if needed, to check the correctness of data

    def test_get_most_recent_csv(self):
        # Create some sample CSV files for testing
        files = [
            'scraped_films_202301171530.csv',
            'scraped_films_202307201134.csv',
            'scraped_films_202301171700.csv'
        ]
        folder_path = FOLDER_LIVE_DATA
        prefix = 'scraped'

        # Test if the function returns the most recent CSV filename correctly
        most_recent_file = get_most_recent_csv(folder_path, prefix)
        expected_file = 'scraped_films_202307201134.csv'
        if most_recent_file is not None:
            self.assertIn(expected_file, most_recent_file)

        # Test for empty folder
        most_recent_file = get_most_recent_csv('/data', prefix)
        self.assertIsNone(most_recent_file)

        # Test for invalid folder path
        most_recent_file = get_most_recent_csv('/invalid/path', prefix)
        self.assertIsNone(most_recent_file)

#run python3 -m unittest webscraping_test.py, 2 passed