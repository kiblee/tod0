# Oauth settings
import os
import pickle
import time

import yaml
from requests_oauthlib import OAuth2Session

settings = {
    "redirect": "https://localhost/login/authorized",
    "scopes": "openid offline_access tasks.readwrite",
    "authority": "https://login.microsoftonline.com/common",
    "authorize_endpoint": "/oauth2/v2.0/authorize",
    "token_endpoint": "/oauth2/v2.0/token",
}

# Code taken from https://docs.microsoft.com/en-us/graph/tutorials/python?tutorial-step=3

# This is necessary because Azure does not guarantee
# to return scopes in the same case and order as requested
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
os.environ["OAUTHLIB_IGNORE_SCOPE_CHANGE"] = "1"

redirect = settings["redirect"]
scope = settings["scopes"]

authorize_url = "{0}{1}".format(settings["authority"], settings["authorize_endpoint"])
token_url = "{0}{1}".format(settings["authority"], settings["token_endpoint"])

# User settings location
config_dir = "{}/.config/tod0".format(os.path.expanduser("~"))
if not os.path.isdir(config_dir):
    os.makedirs(config_dir)


def check_keys(keys):
    client_id = keys["client_id"]
    client_secret = keys["client_secret"]

    if client_id == "" or client_secret == "":
        print(
            "Please enter your client id and secret in {}".format(
                os.path.join(config_dir, "keys.yml")
            )
        )
        print(
            "Instructions to getting your API client id and secret can be found here:\n{}".format(
                "https://github.com/kiblee/tod0/blob/master/GET_KEY.md"
            )
        )
        exit()


# Check for api keys
keys_path = os.path.join(config_dir, "keys.yml")
if not os.path.isfile(keys_path):
    keys = {"client_id": "", "client_secret": ""}

    with open(keys_path, "w") as f:
        yaml.dump(keys, f)
    check_keys(keys)
else:
    # Load api keys
    with open(keys_path) as f:
        keys = yaml.load(f, yaml.SafeLoader)
        check_keys(keys)

client_id = keys["client_id"]
client_secret = keys["client_secret"]


def get_token():
    try:
        # Try to load token from local
        with open(os.path.join(config_dir, "token.pkl"), "rb") as f:
            token = pickle.load(f)

        token = refresh_token(token)

    except Exception:
        # Authorize user to get token
        outlook = OAuth2Session(client_id, scope=scope, redirect_uri=redirect)

        # Redirect  the user owner to the OAuth provider
        authorization_url, state = outlook.authorization_url(authorize_url)
        print("Please go here and authorize:\n", authorization_url)

        # Get the authorization verifier code from the callback url
        redirect_response = input("Paste the full redirect URL below:\n")

        # Fetch the access token
        token = outlook.fetch_token(
            token_url,
            client_secret=client_secret,
            authorization_response=redirect_response,
        )

    store_token(token)
    return token


def store_token(token):
    with open(os.path.join(config_dir, "token.pkl"), "wb") as f:
        pickle.dump(token, f)


def refresh_token(token):
    # Check expiration
    now = time.time()
    # Subtract 5 minutes from expiration to account for clock skew
    expire_time = token["expires_at"] - 300
    if now >= expire_time:
        # Refresh the token
        aad_auth = OAuth2Session(
            client_id, token=token, scope=scope, redirect_uri=redirect
        )

        refresh_params = {"client_id": client_id, "client_secret": client_secret}

        new_token = aad_auth.refresh_token(token_url, **refresh_params)
        return new_token

    # Token still valid, just return it
    return token


def get_oauth_session():
    token = get_token()
    return OAuth2Session(client_id, scope=scope, token=token)
