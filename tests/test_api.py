import pytest
from django.urls import reverse
from django.test.client import Client


@pytest.mark.parametrize('method, expected_result', [
    ('get', 200),
    ('post', 405),
    ('delete', 405),
    ('put', 405)
]
                         )
def test_ping(method, expected_result):
    client = Client()
    response = getattr(client, method)(
        reverse("api:ping"),
        content_type="application/json"
    )
    assert response.status_code == expected_result
    if response.status_code == 200:
        assert response.json() == {"response": "pong"}


def test_auth_bad_creds(db):
    client = Client()
    response = client.post(
        reverse("api:auth"),
        content_type="application/json",
        data={
            "engine": "email",
            "credentials": {
                "email": "some@email",
                "password": "StrongPassword",
            },
        },
    )
    assert response.status_code == 401


@pytest.mark.parametrize('method, expected_result', [
    ('get', 200),
    ('post', 405),
    ('delete', 405),
    ('put', 405)
]
                         )
def test_app_version(db, method, expected_result):
    client = Client()
    response = getattr(client, method)(
        reverse("api:app_versions"),
        content_type="application/json"
    )
    assert response.status_code == expected_result


def test_handbook_list_view(db):
    client = Client()
    response = client.get(reverse("api:handbooks_list"),
                          content_type="application/json"
                          )
    assert response.status_code == 200
    assert response.json()
    assert "configs" in response.json()


@pytest.mark.parametrize('param, expected_code, expected_chunk_result', [
    ("configs", 200, "description"),
    ("test", 404, "error_message")
]
                         )
def test_handbook_view(db, param, expected_code, expected_chunk_result):
    client = Client()
    response = client.get(reverse("api:handbooks_item_list", args=(param,)),
                          content_type="application/json"
                          )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert expected_chunk_result in response.json()[0]
    else:
        assert expected_chunk_result in response.json()


@pytest.mark.parametrize('engine, credentials, expected_code, expected_message', [
    ("test", "pass", 400, "Unknown auth engine='test'"),
    ("email", "pass", 400, "Invalid data type for param credentials"),
    ("email", {"email": "pass@email", "password": "pass"}, 401, "User password or email is not valid"),
    ("email", {"email": "", "password": 400}, 401, "User password or email is not valid"),
    ("email", {"email": "super_admin@example.com", "password": "StrongPass777"}, 200, None)

]
                         )
def test_auth_register_view(db, engine, credentials, expected_code, expected_message):
    client = Client()
    response = client.post(reverse("api:auth"),
                           {"engine": engine, "credentials": credentials},
                           content_type="application/json"
                           )
    assert response.status_code == expected_code
    assert response.json().get("error_message") == expected_message
    if response.status_code == 200:
        assert "access_token" in response.json()


@pytest.mark.parametrize('email, password, expected_code', [
    ('super_admin@example.com', 'StrongPass777', 200)
]
                         )
def test_user_view(db, get_auth, email, password, expected_code):
    headers, user_id, client = get_auth
    response = client.get(reverse("api:user", args=(user_id,)),
                          headers=headers,
                          content_type="application/json")
    assert response.status_code == expected_code
    assert response.json()["email"] == email
    assert response.json()["user_id"] == user_id


@pytest.mark.parametrize('param, expected_result', [
    (123, "Invalid value for uuid field"),
    ("test", "Invalid value for uuid field")

]
                         )
def test_user_view_bad_query_string(db, param, expected_result):
    client = Client()
    response = client.get(reverse("api:user", args=(param,)))
    assert response.status_code == 400
    assert response.json()['error_message'] == expected_result


@pytest.mark.parametrize('email, password, expected_code', [
                        ('super_admin@example.com', 'StrongPass777', 200)
]
                         )
def test_store_exchange_rates_view(db, get_auth, email, password, expected_code):
    headers, user_id, client = get_auth
    response = client.post(reverse("api:store_exchanges_rates"),
                           headers=headers,
                           content_type="application/json")
    assert response.status_code == 201
