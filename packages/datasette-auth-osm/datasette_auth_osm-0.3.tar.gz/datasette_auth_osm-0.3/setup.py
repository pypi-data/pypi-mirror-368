from setuptools import setup
import os

VERSION = "0.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-auth-osm",
    description="Datasette plugin that authenticates users against Openstreetmap",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Andreas Madsack",
    url="https://github.com/mfa/datasette-auth-osm",
    project_urls={
        "Issues": "https://github.com/mfa/datasette-auth-osm/issues",
        "CI": "https://github.com/mfa/datasette-auth-osm/actions",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License"
    ],
    version=VERSION,
    packages=["datasette_auth_osm"],
    entry_points={"datasette": ["auth_osm = datasette_auth_osm"]},
    install_requires=["datasette", "python-baseconv"],
    extras_require={"test": ["pytest", "pytest-asyncio", "pytest-httpx"]},
    python_requires=">=3.7",
)
