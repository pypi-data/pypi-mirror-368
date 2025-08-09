import secrets
import time
from urllib.parse import urlencode

import baseconv
import httpx
from datasette import Response, hookimpl


async def osm_login(request, datasette):
    redirect_uri = datasette.absolute_url(
        request, datasette.urls.path("/-/osm-callback")
    )
    # be sure to use https
    redirect_uri = redirect_uri.replace("http://", "https://")
    try:
        config = _config(datasette)
    except ConfigError as e:
        return _error(datasette, request, str(e))
    state = secrets.token_hex(16)
    url = "https://www.openstreetmap.org/oauth2/authorize?" + urlencode(
        {
            "response_type": "code",
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": "read_prefs",
            "state": state,
        }
    )
    response = Response.redirect(url)
    response.set_cookie("osm-state", state, max_age=3600)
    return response


async def osm_callback(request, datasette):
    try:
        config = _config(datasette)
    except ConfigError as e:
        return _error(datasette, request, str(e))
    code = request.args["code"]
    state = request.args.get("state") or ""
    # Compare state to their cookie
    expected_state = request.cookies.get("osm-state") or ""
    if not state or not secrets.compare_digest(state, expected_state):
        return _error(
            datasette,
            request,
            "state check failed, your authentication request is no longer valid",
        )

    # Exchange the code for an access token
    response = httpx.post(
        "https://www.openstreetmap.org/oauth2/token",
        data={
            "grant_type": "authorization_code",
            "redirect_uri": datasette.absolute_url(
                request, datasette.urls.path("/-/osm-callback")
            ),
            "code": code,
        },
        auth=(config["client_id"], config["client_secret"]),
    )
    if response.status_code != 200:
        return _error(
            datasette,
            request,
            "Could not obtain access token: {}".format(response.status_code),
        )
    # This should have returned an access token
    access_token = response.json()["access_token"]
    # Use access token to get user details
    profile_response = httpx.get(
        "https://www.openstreetmap.org/api/0.6/user/details.json",
        headers={"Authorization": "Bearer {}".format(access_token)},
    )
    if profile_response.status_code != 200:
        return _error(
            datasette,
            request,
            "Could not fetch profile: {}".format(response.status_code),
        )
    # Set actor cookie and redirect to homepage
    redirect_response = Response.redirect("/")
    expires_at = int(time.time()) + (24 * 60 * 60)
    user = profile_response.json().get("user")
    redirect_response.set_cookie(
        "ds_actor",
        datasette.sign(
            {
                "a": {"display": user.get("display_name"), "osm_id": user.get("id")},
                "e": baseconv.base62.encode(expires_at),
            },
            "actor",
        ),
    )
    return redirect_response


@hookimpl
def register_routes():
    return [
        (r"^/-/osm-login$", osm_login),
        (r"^/-/osm-callback$", osm_callback),
    ]


class ConfigError(Exception):
    pass


def _config(datasette):
    config = datasette.plugin_config("datasette-auth-osm")
    missing = [key for key in ("client_id", "client_secret") if not config.get(key)]
    if missing:
        raise ConfigError(
            "The following osm plugin settings are missing: {}".format(
                ", ".join(missing)
            )
        )
    return config


def _error(datasette, request, message):
    datasette.add_message(request, message, datasette.ERROR)
    return Response.redirect("/")


@hookimpl
def menu_links(datasette, actor):
    if not actor:
        return [
            {
                "href": datasette.urls.path("/-/osm-login"),
                "label": "Sign in with OpenStreetMap",
            },
        ]
