"""Utils module."""

from megalus.utils import get_ngrok_url


def test_get_ngrok_url(mocker, ngrok_response):
    """Test Get Ngrok URL."""
    ngrok_dict = {
        "port": 6544,
        "secure": False,
        "env": "MEGALUS_NGROK_TEST_ENV"
    }
    mocker.patch('megalus.utils.requests.get', return_value=ngrok_response)
    data = get_ngrok_url(ngrok_dict)

    expect_url = "http://87f3557f.ngrok.io"
    assert data == expect_url
