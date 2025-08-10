from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

packages = ['flask_login_dictabase_blueprint'] # the local filesystem package path

setup(
    name="flask_login_dictabase_blueprint",

    version="2.0.0",  # updated to pep8 style guide, added get_app() function for ease of use

    packages=packages,
    install_requires=[
        'flask',
        'flask-dictabase',
        'flask-login',
    ],

    author="Grant miller",
    author_email="grant@grant-miller.com",
    description="A Flask Blueprint for managing users.",
    long_description=long_description,
    license="PSF",
    keywords="grant miller flask blueprint dictabase login user management",
    url="https://github.com/GrantGMiller/blueprint_flask_login_dictabase",  # project home page, if any
    project_urls={
        "Source Code": "https://github.com/GrantGMiller/blueprint_flask_login_dictabase",
    }

)
