import django.urls
import pytest
from django.urls import resolve
from api.views import __all__ as views_list

endpoints = [
         'version',
         'ping',
         'handbooks',
         'handbooks/test',
         'auth/auth',
         'users/1',
         'services/store-rates'
     ]


@pytest.mark.parametrize('view, endpoint', zip(views_list, endpoints)
                         )
def test_path(view, endpoint):
    assert resolve('/api/' + endpoint + '/').func.__name__ == view
