from datetime import UTC, datetime
from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    response_data = response.json()

    created_at = response_data['created_at']
    update_at = response_data['update_at']
    now = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M')

    assert response.status_code == HTTPStatus.CREATED

    assert response_data['username'] == 'alice'
    assert response_data['email'] == 'alice@example.com'
    assert response_data['id'] == 1
    assert created_at.startswith(now)
    assert update_at.startswith(now)


# def test_create_user_already_existing(client, user):
#     response = client.post(
#         '/users/',
#         json={
#             'username': 'Teste',
#             'email': 'bla@bla.com',
#             'password': 'testtest',
#         },
#     )
#     assert response.status_code == HTTPStatus.BAD_REQUEST


# def test_create_email_already_existing(client, user):
#     response = client.post(
#         '/users/',
#         json={
#             'username': 'Bla',
#             'email': 'teste@test.com',
#             'password': 'testtest',
#         },
#     )
#     assert response.status_code == HTTPStatus.BAD_REQUEST


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    user_schema['created_at'] = datetime.strftime(
        user_schema['created_at'], '%Y-%m-%dT%H:%M:%S'
    )
    user_schema['update_at'] = datetime.strftime(
        user_schema['update_at'], '%Y-%m-%dT%H:%M:%S'
    )
    response_data = response.json()

    created_at = response_data['users'][0]['created_at']
    update_at = response_data['users'][0]['update_at']
    now = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M')

    assert created_at.startswith(now)
    assert update_at.startswith(now)
    assert response_data['users'][0]['username'] == user_schema['username']
    assert response_data['users'][0]['email'] == user_schema['email']
    assert response_data['users'][0]['id'] == user_schema['id']


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    response_data = response.json()

    created_at = response_data['created_at']
    update_at = response_data['update_at']
    now = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M')

    assert response.status_code == HTTPStatus.OK
    assert created_at.startswith(now)
    assert update_at.startswith(now)
    assert response_data['username'] == 'bob'
    assert response_data['email'] == 'bob@example.com'
    assert response_data['id'] == 1


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
