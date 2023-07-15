import pytest
import pandas as pd
from preprocessing import (
    convert_duration_to_minutes,
    remove_parasite_chars,
    drop_rows_with_excessive_missing_values
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
