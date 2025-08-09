import base64
import urllib

import pytest
from datasette.app import Datasette


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-auth-osm" in installed_plugins


@pytest.fixture
def non_mocked_hosts():
    # https://docs.datasette.io/en/stable/testing_plugins.html#testing-outbound-http-calls-with-pytest-httpx
    return ["localhost"]


@pytest.fixture
def datasette():
    return Datasette(
        [],
        memory=True,
        metadata={
            "plugins": {
                "datasette-auth-osm": {
                    "client_id": "CLIENT_ID",
                    "client_secret": "CLIENT_SECRET",
                }
            }
        },
    )


@pytest.mark.asyncio
async def test_auth0_login(datasette):
    response = await datasette.client.get("/-/osm-login")
    assert response.status_code == 302
    location = response.headers["location"]
    bits = urllib.parse.urlparse(location)
    assert bits.netloc == "www.openstreetmap.org"
    assert bits.path == "/oauth2/authorize"
    qs = dict(urllib.parse.parse_qsl(bits.query))
    assert (
        qs.items()
        >= {
            "response_type": "code",
            "client_id": "CLIENT_ID",
            "redirect_uri": "http://localhost/-/osm-callback",
            "scope": "read_prefs",
        }.items()
    )
    # state should be a random string
    assert len(qs["state"]) == 32


@pytest.mark.asyncio
async def test_callback(datasette, httpx_mock):
    httpx_mock.add_response(
        url="https://www.openstreetmap.org/oauth2/token",
        json={"access_token": "ACCESS_TOKEN"},
    )
    httpx_mock.add_response(
        url="https://www.openstreetmap.org/api/0.6/user/details.json",
        json={"user": {"id": "1234", "display_name": "test"}},
    )
    response = await datasette.client.get(
        "/-/osm-callback?state=state&code=x", cookies={"osm-state": "state"}
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/"
    assert datasette.unsign(response.cookies["ds_actor"], "actor")["a"] == {
        "osm_id": "1234",
        "display": "test",
    }
    post_request, get_request = httpx_mock.get_requests()
    # post should have had client ID / secret in Authorization
    assert post_request.headers["authorization"] == "Basic {}".format(
        base64.b64encode(b"CLIENT_ID:CLIENT_SECRET").decode("utf-8")
    )
    # get should have used the access token
    assert get_request.headers["authorization"] == "Bearer ACCESS_TOKEN"


@pytest.mark.asyncio
async def test_callback_state_must_match(datasette):
    state = "state1234"
    response = await datasette.client.get(
        "/-/osm-callback?state=not-the-same&code=x", cookies={"osm-state": state}
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/"
    assert_message(
        datasette,
        response,
        "state check failed, your authentication request is no longer valid",
    )


def assert_message(datasette, response, message):
    assert datasette.unsign(response.cookies["ds_messages"], "messages") == [
        [message, 3]
    ]
