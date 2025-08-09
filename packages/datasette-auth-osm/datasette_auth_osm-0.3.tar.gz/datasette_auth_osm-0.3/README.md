# datasette-auth-osm

[![PyPI](https://img.shields.io/pypi/v/datasette-auth-osm.svg)](https://pypi.org/project/datasette-auth-osm/)
[![Tests](https://github.com/mfa/datasette-auth-osm/workflows/Test/badge.svg)](https://github.com/mfa/datasette-auth-osm/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mfa/datasette-auth-osm/blob/main/LICENSE)

Datasette plugin that authenticates users against OpenStreetMap

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-auth-osm

## Demo

You can try this out at [datasette-auth-osm.madflex.de](https://datasette-auth-osm.madflex.de/) - click on the top right menu icon and select "Sign in with OpenStreetMap".

## Initial configuration

First, create a new application in [Openstreetmap - OAuth2 Applications](https://www.openstreetmap.org/oauth2/applications).
You will need the client ID and client secret for that application.

Add `http://127.0.0.1:8001/-/osm-callback` to the list of Allowed Callback URLs.

Then configure these plugin secrets using `metadata.yml`:

```yaml
plugins:
  datasette-auth-osm:
    client_id:
      "$env": OSM_CLIENT_ID
    client_secret:
      "$env": OSM_CLIENT_SECRET
```

In development, you can run Datasette and pass in environment variables like this:
```
OSM_CLIENT_ID="...client-id-goes-here..." \
OSM_CLIENT_SECRET="...secret-goes-here..." \
datasette -m metadata.yml
```

If you are deploying using `datasette publish` you can pass these using `--plugin-secret`. For example, to deploy using Cloud Run you might run the following:
```
datasette publish cloudrun mydatabase.db \
--install datasette-auth-osm \
--plugin-secret datasette-auth-osm client_id "your-client-id" \
--plugin-secret datasette-auth-osm client_secret "your-client-secret" \
--service datasette-auth-osm-demo
```
Once your Datasette instance is deployed, you will need to add its callback URL to the "Allowed Callback URLs" list your [OAuth2 application](https://www.openstreetmap.org/oauth2/applications) in OpenStreetMap.

The callback URL should be something like:

    https://url-to-your-datasette/-/osm-callback


## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-auth-osm
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
