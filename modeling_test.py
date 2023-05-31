import pytest
from modeling import get_closest_film_title

@pytest.fixture
def film_titles():
    # Sample movie titles for unit testing
    return ['Dune', 'Parasite', 'Tazza']

def test_get_closest_movie_title(film_titles):
    # Handling the case when input title is similar
    suggestion = get_closest_film_title('Dunz', film_titles)
    assert suggestion == 'Dune'
    # Handling the case when input title has no matches
    suggestion = get_closest_film_title('Movie 4', film_titles)
    assert suggestion is None
    # Handling the case when input title matches one of the film
    suggestion = get_closest_film_title('Parasite', film_titles)
    assert suggestion == 'Parasite'


# run pytest -v
