import os
import time
import json
import pickle
import yaml
from requests_oauthlib import OAuth2Session


# Oauth settings
settings = {}
settings["redirect"] = "https://localhost/login/authorized"
settings["scopes"] = "openid offline_access tasks.readwrite"
settings["authority"] = "https://login.microsoftonline.com/common"
settings["authorize_endpoint"] = "/oauth2/v2.0/authorize"
settings["token_endpoint"] = "/oauth2/v2.0/token"


def check_keys(keys):
    client_id = keys["client_id"]
    client_secret = keys["client_secret"]

    if client_id == "" or client_secret == "":
        print(
            "Please enter your client id and secret in {}".format(
                os.path.join(config_dir, "keys.yml")
            )
        )
        exit()


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

        # Fetch a protected resource, i.e. calendar information
        # o = outlook.get('{}/tasks'.format(base_api_url))
        # print(o.content)

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

        refresh_params = {
            "client_id": client_id,
            "client_secret": client_secret,
        }

        new_token = aad_auth.refresh_token(token_url, **refresh_params)
        return new_token

    # Token still valid, just return it
    return token


def parse_contents(response):
    return json.loads(response.content.decode())["value"]


def list_tasks(all_=False, folder=""):
    token = get_token()
    outlook = OAuth2Session(client_id, scope=scope, token=token)

    if folder == "":
        if all_:
            o = outlook.get("{}/tasks".format(base_api_url))
        else:
            o = outlook.get(
                "{}/tasks?filter=status ne 'completed'".format(base_api_url)
            )
    else:
        if all_:
            o = outlook.get("{}/taskFolders/{}/tasks".format(base_api_url, folder))
        else:
            o = outlook.get(
                "{}/taskFolders/{}/tasks?filter=status ne 'completed'".format(
                    base_api_url, folder
                )
            )

    return parse_contents(o)


def list_and_update_folders():
    token = get_token()
    outlook = OAuth2Session(client_id, scope=scope, token=token)
    o = outlook.get("{}/taskFolders".format(base_api_url))
    contents = parse_contents(o)

    # Cache folders
    name2id = {}
    id2name = {}

    folders = parse_contents(o)
    for f in folders:
        name2id[f["name"]] = f["id"]
        id2name[f["id"]] = f["name"]

    with open(os.path.join(config_dir, "folder_name2id.pkl"), "wb") as f:
        pickle.dump(name2id, f)
    with open(os.path.join(config_dir, "folder_id2name.pkl"), "wb") as f:
        pickle.dump(id2name, f)

    return contents


def create_task(text, folder=None):
    """Create task with subject `text`"""
    token = get_token()
    outlook = OAuth2Session(client_id, scope=scope, token=token)

    # Fill request body
    request_body = {}
    request_body["subject"] = text

    if folder is None:
        o = outlook.post("{}/tasks".format(base_api_url), json=request_body)
    else:
        o = outlook.post(
            "{}/taskFolders/{}/tasks".format(base_api_url, folder), json=request_body
        )

    return o.ok


def delete_task(task_id):
    token = get_token()
    outlook = OAuth2Session(client_id, scope=scope, token=token)
    o = outlook.delete("{}/tasks/{}".format(base_api_url, task_id))
    return o.ok


def complete_task(task_id):
    token = get_token()
    outlook = OAuth2Session(client_id, scope=scope, token=token)
    o = outlook.post("{}/tasks/{}/complete".format(base_api_url, task_id))
    return o.ok


# Code taken from https://docs.microsoft.com/en-us/graph/tutorials/python?tutorial-step=3

# This is necessary because Azure does not guarantee
# to return scopes in the same case and order as requested
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
os.environ["OAUTHLIB_IGNORE_SCOPE_CHANGE"] = "1"

redirect = settings["redirect"]
scope = settings["scopes"]

authorize_url = "{0}{1}".format(settings["authority"], settings["authorize_endpoint"])
token_url = "{0}{1}".format(settings["authority"], settings["token_endpoint"])

base_api_url = "https://graph.microsoft.com/beta/me/outlook/"

# User settings location
config_dir = "{}/.config/tod0".format(os.path.expanduser("~"))
if not os.path.isdir(config_dir):
    os.makedirs(config_dir)

# Check for api keys
keys_path = os.path.join(config_dir, "keys.yml")
if not os.path.isfile(keys_path):
    keys = {}
    keys["client_id"] = ""
    keys["client_secret"] = ""
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
