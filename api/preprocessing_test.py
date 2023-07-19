import pytest
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from preprocessing import (
    convert_duration_to_minutes,
    remove_parasite_chars,
    drop_rows_with_missing_values
)

# Unit test for the convert_duration_to_minutes function
def test_convert_duration_to_minutes():
    assert convert_duration_to_minutes('1h 30min') == 90
    assert convert_duration_to_minutes('2h') == 120
    assert convert_duration_to_minutes('45min') == 45
    assert convert_duration_to_minutes('') == 0

# Unit test for the remove_parasite_chars function
def test_remove_parasite_chars():
    assert remove_parasite_chars('Avec\nActor\n') == 'Actor'
    assert remove_parasite_chars('De\nDirector\n') == 'Director'
    assert remove_parasite_chars('\nSample\nText\n') == 'SampleText'
    assert remove_parasite_chars('No Parasite Chars') == 'No Parasite Chars'

# TODO: add a Unit test for the drop_rows_with_missing_values function
"""def test_drop_rows_with_missing_values():
    # Create a sample DataFrame with missing values
    df = pd.DataFrame({
        'title': ['John Wick', 'Barbie', None],
        'duration': [120, 45, None],
        'genres': ['Action', 'Comedy', 'Thriller'],
        'directors': ['Pablo', None, 'Myself'],
        'cast': ['Keanu Reeves', 'Margot Robbie', None],
        'synopsis': ['Pew Pew', 'Barbie and Ken', None],
        'rating': [4.9, 4.1, None]
    })

    # Specify the content features to drop rows with missing values
    content_features = ['genres', 'directors']

    # Call the function under test
    df_cleaned = drop_rows_with_missing_values(df, content_features)

    # Assert that the returned DataFrame is as expected
    expected_df = pd.DataFrame({
        'title': ['John Wick', None],
        'duration': [120, None],
        'genres': ['Action', 'Thriller'],
        'directors': ['Pablo', 'Myself'],
        'cast': ['Keanu Reeves', None],
        'synopsis': ['Pew Pew', None],
        'rating': [4.9, None]
    })

    # Reset the indices so that they are aligned correctly before the comparison
    df_cleaned = df_cleaned.reset_index(drop=True)
    expected_df = expected_df.reset_index(drop=True)

    pd.testing.assert_frame_equal(df_cleaned, expected_df)

    # Assert that the number of rows has decreased
    assert len(df_cleaned) < len(df)"""
    
# run pytest, 3 passed

