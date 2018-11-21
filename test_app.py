import pytest
from app import app
import time


@pytest.fixture
def client():
    client = app.test_client()
    yield client


def test_page(client):
    rv = client.get('/')
    assert '<div class="flex-container">' in str(rv.data)
    assert '2006-01-02' in str(rv.data)


def test_update(client):
    # make sure this month or last months data is present
    rv = client.get('/update')
    datestamp = time.strftime("%m/%Y")
    last_month = '/', (int(datestamp[0:2]) - 1), '/'
    assert datestamp or last_month in str(rv.data)


def test_clean(client):
    rv = client.get('/clean')
    assert '806  19/11/2018  127.67  136.40   57.95   57.95    20.0    20.0' in str(rv.data)


def test_date(client):
    rv = client.get('/date')
    assert '806  2018-11-19      127.67      136.40  57.95  57.95  20.0  20.0' in str(rv.data)


def test_inflation(client):
    rv = client.get('/inflation')
    assert "[[&#39;2018-09&#39;], [&#39;2.2&#39;]]" in str(rv.data)

# def test_inflation_adjusted(client):
#     rv = client.get('/adjusted')
