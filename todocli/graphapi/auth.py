import json
import os
import pickle

from todocli.graphapi.oauth import get_oauth_session, config_dir

base_api_url = "https://graph.microsoft.com/v1.0/me/todo"


def parse_contents(response):
    return json.loads(response.content.decode())["value"]


def list_tasks(all_=False, folder=""):
    outlook = get_oauth_session()

    if folder == "":
        if all_:
            o = outlook.get("{}/tasks?top=100".format(base_api_url))
        else:
            o = outlook.get(
                "{}/tasks?$filter=status ne 'completed'&top=100".format(base_api_url)
            )
    else:
        if all_:
            o = outlook.get("{}/lists/{}/tasks?top=100".format(base_api_url, folder))
        else:
            o = outlook.get(
                "{}/lists/{}/tasks?$filter=status ne 'completed'&top=100".format(
                    base_api_url, folder
                )
            )

    return parse_contents(o)


def list_and_update_folders():
    outlook = get_oauth_session()
    o = outlook.get("{}/lists?top=20".format(base_api_url))
    contents = parse_contents(o)

    # Cache folders
    name2id = {}
    id2name = {}

    folders = parse_contents(o)
    for f in folders:
        name2id[f["displayName"]] = f["id"]
        id2name[f["id"]] = f["displayName"]

    with open(os.path.join(config_dir, "folder_name2id.pkl"), "wb") as f:
        pickle.dump(name2id, f)
    with open(os.path.join(config_dir, "folder_id2name.pkl"), "wb") as f:
        pickle.dump(id2name, f)

    return contents


def create_folder(name):
    """Create folder with name `name`"""
    outlook = get_oauth_session()

    # Fill request body
    request_body = {"name": name}

    o = outlook.post("{}/lists".format(base_api_url), json=request_body)

    return o.ok


def delete_folder(folder_id):
    """Delete folder with id `folder_id`"""
    outlook = get_oauth_session()
    o = outlook.delete("{}/lists/{}".format(base_api_url, folder_id))
    return o.ok


def create_task(text, folder=None):
    """Create task with subject `text`"""
    outlook = get_oauth_session()

    # Fill request body
    request_body = {"title": text}

    if folder is None:
        o = outlook.post("{}/tasks".format(base_api_url), json=request_body)
    else:
        o = outlook.post(
            "{}/lists/{}/tasks".format(base_api_url, folder), json=request_body
        )

    return o.ok


def delete_task(task_id):
    outlook = get_oauth_session()

    o = outlook.delete("{}/tasks/{}".format(base_api_url, task_id))
    return o.ok


def complete_task(list_id, task_id):
    outlook = get_oauth_session()

    o = outlook.patch(
        "{}/lists/{}/tasks/{}/".format(base_api_url, list_id, task_id),
        json={"status": "completed"},
    )
    return o.ok
