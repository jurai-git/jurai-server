
advogado_create_data = {
    'username': 'test_advogado',
    'email': 'test_advogado@test.com',
    'oab': 'test_advogado',
    'password': 'test_advogado'
}

def test_create_advogado(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

def test_create_advogado_with_conflicting_username(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/new', json={'username': advogado_create_data['username'], 'oab': '123123', 'password': '12341234', 'email': 'test@test.com'})
    assert response.status_code == 409
    assert response.json['message'] == 'ERROR_CONFLICT'
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].oab == advogado_create_data['oab']

def test_create_advogado_with_conflicting_username_case_insensitive(client, app):
    """usernames should be case-insensitive (USER and user are the same), and they should conflict like that"""
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/new', json={'username': advogado_create_data['username'].upper(), 'oab': '123123', 'password': '12341234', 'email': 'test@test.com'})
    assert response.status_code == 409
    assert response.json['message'] == 'ERROR_CONFLICT'
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].oab == advogado_create_data['oab']

def test_create_advogado_with_empty_fields(client, app):
    response = client.post('/advogado/new', json={'username': '', 'oab': '', 'password': '', 'email': ''})
    assert response.status_code == 400
    assert response.json['message'] == 'ERROR_REQUIRED_FIELDS_EMPTY'

    advogados = app.extensions['advogado_service'].get_all()
    assert len(advogados) == 0

def test_auth_advogado_with_token(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    print(response.json)
    assert response.json['advogado']['username'] == advogado_create_data['username']
    assert response.json['message'] == 'SUCCESS'

def test_auth_advogado_with_invalid_token(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer 1234'})
    assert response.status_code == 401 or response.status_code == 400
    print(response.json)
    assert response.json['message'] != 'SUCCESS'

def test_auth_advogado_without_token(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/get', json={})
    assert response.status_code == 401 or response.status_code == 400
    print(response.json)
    assert response.json['message'] != 'SUCCESS'

def test_auth_advogado_with_password(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/get', json={'username': advogado_create_data['username'], 'password': advogado_create_data['password']})
    assert response.status_code == 200
    print(response.json)
    assert response.json['advogado']['access_token'] == token

def test_auth_advogado_with_invalid_password(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/get', json={'username': advogado_create_data['username'], 'password': '123456789InvalidPassword123'})
    assert response.status_code == 401 or response.status_code == 400
    print(response.json)
    assert response.json['message'] != 'SUCCESS'
    assert 'advogado' not in response.json


def test_auth_advogado_without_password(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/get', json={'username': advogado_create_data['username']})
    assert response.status_code == 401 or response.status_code == 400
    print(response.json)
    assert response.json['message'] != 'SUCCESS'
    assert 'advogado' not in response.json

def test_auth_advogado_with_password_and_token(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.post('/advogado/get', json={'username': advogado_create_data['username'], 'password': advogado_create_data['password']}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    print(response.json)
    assert response.json['message'] == 'SUCCESS'
    assert response.json['advogado']['access_token'] == token


def test_delete_advogado(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.delete("/advogado/delete", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 2
    assert response.json['message'] == 'SUCCESS'
    advogados = service.get_all()
    assert len(advogados) == 0

def test_delete_advogado_without_token(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.delete("/advogado/delete")
    assert response.status_code // 100 == 4
    advogados = service.get_all()
    assert len(advogados) == 1

def test_delete_advogado_with_invalid_token(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    response = client.delete("/advogado/delete", headers={'Authorization': 'Bearer InvalidToken1234'})
    assert response.status_code // 100 == 4
    advogados = service.get_all()
    assert len(advogados) == 1

def test_delete_nonexistent_advogado(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    service = app.extensions['advogado_service']
    advogados = service.get_all()
    assert len(advogados) == 1
    assert advogados[0].username == advogado_create_data['username']

    # first deletion should work
    response = client.delete("/advogado/delete", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 2
    assert response.json['message'] == 'SUCCESS'
    advogados = service.get_all()
    assert len(advogados) == 0

    # second deletion should return 401 (no advogado found with the bearer token)
    response = client.delete("/advogado/delete", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    assert response.json['message'] == 'ERROR_INVALID_CREDENTIALS'


def test_edit_advogado_username(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    response = client.put('/advogado/update', json={'username': 'new_username'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'SUCCESS'

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 2
    assert response.json['advogado']['username'] == 'new_username'


def test_edit_advogado_oab(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    response = client.put('/advogado/update', json={'oab': 'new_oab'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'SUCCESS'

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 2
    assert response.json['advogado']['oab'] == 'new_oab'


def test_edit_advogado_email(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    response = client.put('/advogado/update', json={'email': 'new_email@gmail.com'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'SUCCESS'

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 2
    assert response.json['advogado']['email'] == 'new_email@gmail.com'


def test_edit_advogado_username_and_oab(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    response = client.put('/advogado/update', json={'username': 'new_username', 'oab': 'new_oab'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'SUCCESS'

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 2
    assert response.json['advogado']['username'] == 'new_username'
    assert response.json['advogado']['oab'] == 'new_oab'

def test_edit_advogado_password_invalidates_token(client, app):
    """Changing the advogado's password should invalidate their token"""
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    response = client.put('/advogado/update', json={'password': 'new_password'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'SUCCESS'

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 4
    assert 'advogado' not in response.json

def test_edit_advogado_password(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    response = client.put('/advogado/update', json={'password': 'new_password'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'SUCCESS'

    response = client.post('/advogado/get', json={'username': advogado_create_data['password'], 'password': 'new_password'})
    assert response.status_code // 100 == 2
    assert 'advogado' in response.json
    assert response.json['advogado']['username'] == advogado_create_data['username']

def test_edit_advogado_password_produces_valid_token(client, app):
    """Editing the advogado's password should produce a new valid token"""
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201
    token = response.json['access_token']
    assert token is not None

    response = client.put('/advogado/update', json={'password': 'new_password'},
                          headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'SUCCESS'

    response = client.post('/advogado/get', json={'username': advogado_create_data['username'], 'password': 'new_password'})
    assert response.status_code // 100 == 2
    token = response.json['advogado']['access_token']
    assert token is not None

    response = client.post('/advogado/get', json={}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code // 100 == 2
    assert response.json['advogado']['username'] == advogado_create_data['username']
