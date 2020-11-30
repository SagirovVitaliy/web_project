

def test_home_page_with_fixture(test_client):
    '''
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    '''
    response = test_client.get('/')
    assert response.status_code == 200


def test_sign_up_page_with_fixture(test_client):
    '''
    GIVEN a Flask application configured for testing
    WHEN the '/sign_up' page is requested (GET)
    THEN check that the response is valid
    '''
    response = test_client.get('/sign_up')
    assert response.status_code == 200


def test_sign_in_page_with_fixture(test_client):
    '''
    GIVEN a Flask application configured for testing
    WHEN the '/sign_in' page is requested (GET)
    THEN check that the response is valid
    '''
    response = test_client.get('/sign_in')
    assert response.status_code == 200


def test_sign_out_page_with_fixture(test_client):
    '''
    GIVEN a Flask application configured for testing
    WHEN the '/sign_out' page is requested (GET)
    THEN check that the response is valid
    '''
    response = test_client.get('/sign_out')
    assert response.status_code == 302

