import os
import json
import pickle
from datetime import datetime

from todocli.oauth import getOAuthSession, config_dir
from todocli.parse_contents import parse_contents

base_api_url = "https://graph.microsoft.com/beta/me/outlook/"

def list_tasks(all_=False, folder=""):
    outlook = getOAuthSession()

    if folder == "":
        if all_:
            o = outlook.get("{}/tasks?top=100".format(base_api_url))
        else:
            o = outlook.get(
                "{}/tasks?filter=status ne 'completed'&top=100".format(base_api_url)
            )
    else:
        if all_:
            o = outlook.get(
                "{}/taskFolders/{}/tasks?top=100".format(base_api_url, folder)
            )
        else:
            o = outlook.get(
                "{}/taskFolders/{}/tasks?filter=status ne 'completed'&top=100".format(
                    base_api_url, folder
                )
            )

    return parse_contents(o)


def list_and_update_folders():
    outlook = getOAuthSession()
    o = outlook.get("{}/taskFolders?top=20".format(base_api_url))
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


def create_folder(name):
    """Create folder with name `name`"""
    outlook = getOAuthSession()

    # Fill request body
    request_body = {}
    request_body["name"] = name

    o = outlook.post("{}/taskFolders".format(base_api_url), json=request_body)

    return o.ok


def delete_folder(folder_id):
    """Delete folder with id `folder_id`"""
    outlook = getOAuthSession()
    o = outlook.delete("{}/taskFolders/{}".format(base_api_url, folder_id))
    return o.ok


def create_task(text, folder=None):
    """Create task with subject `text`"""
    outlook = getOAuthSession()

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
    outlook = getOAuthSession()

    o = outlook.delete("{}/tasks/{}".format(base_api_url, task_id))
    return o.ok


def complete_task(task_id):
    outlook = getOAuthSession()

    o = outlook.post("{}/tasks/{}/complete".format(base_api_url, task_id))
    return o.ok