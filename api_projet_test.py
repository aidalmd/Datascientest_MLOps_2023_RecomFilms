from api_projet import get_recommendations

def test_get_recommendations():
    """ La recommandation n'est pas vide """
    assert (len(get_recommendations("Vol au-dessus d'un nid de coucou"))) != 0