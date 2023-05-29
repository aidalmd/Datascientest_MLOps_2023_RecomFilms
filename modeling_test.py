import pytest
from fuzzywuzzy import fuzz
from modeling import get_closest_film_title

@pytest.fixture
def filme_titles():
    # Sample movie titles for testing
    return ['Dune', 'Parasite', 'Tazza']

def test_get_closest_movie_title(filme_titles):
    # Handling the case when input title is similar
    suggestion = get_closest_film_title('Dunz', filme_titles)
    assert suggestion == 'Dune'
    # Handling the case when input title has no matches
    suggestion = get_closest_film_title('Movie 4', filme_titles)
    assert suggestion is None
    # Handling the case when input title matches one of the film
    suggestion = get_closest_film_title('Parasite', filme_titles)
    assert suggestion == 'Parasite'