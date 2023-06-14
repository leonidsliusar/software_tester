import subprocess
import uuid
import importlib
from django.test.client import Client
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse

# SQLAlchemy
from sqlalchemy_utils import drop_database, create_database, database_exists

# Lamb Framework
import lamb.db.session
from lamb.db.session import metadata, lamb_db_session_maker

import pytest

from .factories import *


@pytest.fixture(scope='function')
def db():
    settings.DATABASES["default"]["NAME"] = "test_core"
    importlib.reload(lamb.db.session)
    session = lamb_db_session_maker()

    db_url = session.get_bind().url
    if database_exists(db_url):
        drop_database(db_url)
    create_database(session.get_bind().url)

    session.execute("CREATE EXTENSION pgcrypto")
    session.commit()

    metadata.bind = session.get_bind()
    metadata.create_all()
    # fill_handbooks
    call_command("fill_handbooks")

    session = lamb_db_session_maker()
    AlchemyModelFactory._meta.sqlalchemy_session = session
    yield session
    session.rollback()
    drop_database(db_url)


@pytest.fixture
def get_auth(request):
    email, password = request.getfixturevalue("email"), request.getfixturevalue("password")
    client = Client()
    response = client.post(reverse("api:auth"),
                           {"engine": 'email',
                            "credentials": {"email": email, "password": password}},
                           content_type="application/json"
                           )
    token, user_id = (response.json().get("access_token"), response.json().get("user").get("user_id"))
    token = token.encode('utf-8')
    headers = {"HTTP_X_LAMB_AUTH_TOKEN": token}
    return headers, user_id, client
