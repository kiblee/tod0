import os
import pickle
import click
from todocli import auth


@click.group()
def main():
    pass


@main.command(short_help="list tasks or folders")
@click.option(
    "--all", "-a", "all_", is_flag=True, help="List all tasks including completed ones"
)
@click.option(
    "--filter", "-f", "filter_", default="", help="List tasks from specific folder"
)
@click.option("--folders", is_flag=True, help="List folders")
def list(all_, filter_, folders):
    """List tasks/folders."""

    if folders:
        list_folders()
        return

    if filter_ == "":
        tasks = auth.list_tasks(all_=all_)
    else:
        tasks = auth.list_tasks(all_=all_, folder=folder2id(filter_))

    # Print results
    results = {}
    for idx, t in enumerate(tasks):
        id_ = t["id"]
        subject = t["subject"]
        status = t["status"]
        folder_id = t["parentFolderId"]

        click.echo(
            " {}   {:<20}\t{:<20}\t{}".format(
                click.style(str(idx)),
                click.style(status, fg="green"),
                click.style(id2folder(folder_id) or "-", fg="blue"),
                subject,
            )
        )
        results[str(idx)] = t

    # Save results for use in other commands
    with open(os.path.join(auth.config_dir, "list_results.pkl"), "wb") as f:
        pickle.dump(results, f)


@main.command(short_help="create a task")
@click.option("--filter", "-f", "filter_", default="", help="target folder")
@click.argument("subject", required=True)
def create(subject, filter_):
    """create task with subject SUBJECT."""

    if not filter_:
        ok = auth.create_task(subject)
    else:
        folder_id = folder2id(filter_)
        if folder_id is None:
            click.echo("Folder {} does not exist.".format(filter_), err=True)
            return
        else:
            ok = auth.create_task(subject, folder_id)

    if ok:
        click.echo("New task created: {}".format(subject))
    else:
        click.echo("Oops, something went wrong.")


@main.command(short_help="delete a task")
@click.argument("task_num")
def delete(task_num):
    """Delete task with id TASK_NUM."""

    # Load results from list command
    with open(os.path.join(auth.config_dir, "list_results.pkl"), "rb") as f:
        results = pickle.load(f)

    if task_num not in results:
        click.echo("Task {} does not exist.".format(task_num))
    else:
        task = results[task_num]
        if click.confirm("Delete task? {}".format(task["subject"])):
            ok = auth.delete_task(task["id"])
            if ok:
                click.echo("Done.")
            else:
                click.echo("Oops, something went wrong.")


@main.command(short_help="mark task as completed")
@click.argument("task_num")
def complete(task_num):
    """Mark task TASK_NUM as completed."""

    # Load results from list command
    with open(os.path.join(auth.config_dir, "list_results.pkl"), "rb") as f:
        results = pickle.load(f)

    if task_num not in results:
        click.echo("Task {} does not exist.".format(task_num))
    else:
        task = results[task_num]
        if click.confirm("Mark task as complete? {}".format(task["subject"])):
            ok = auth.complete_task(task["id"])
            if ok:
                click.echo("Done.")
            else:
                click.echo("Oops, something went wrong.")


def folder2id(folder):
    """Maps folder name to id"""

    cache_path = os.path.join(auth.config_dir, "folder_name2id.pkl")
    if not os.path.isfile(cache_path):
        auth.list_and_update_folders()

    with open(cache_path, "rb") as f:
        name2id = pickle.load(f)

    # Update cache if folder doesn't exist
    if folder not in name2id:
        auth.list_and_update_folders()
        with open(cache_path, "rb") as f:
            name2id = pickle.load(f)

    return name2id.get(folder)


def id2folder(id_):
    """Maps id to folder name"""

    cache_path = os.path.join(auth.config_dir, "folder_id2name.pkl")
    if not os.path.isfile(cache_path):
        auth.list_and_update_folders()

    with open(cache_path, "rb") as f:
        id2name = pickle.load(f)

    # Update cache if id doesn't exist
    if id_ not in id2name:
        auth.list_and_update_folders()
        with open(cache_path, "rb") as f:
            id2name = pickle.load(f)

    return id2name.get(id_)


def list_folders():
    folders = auth.list_and_update_folders()
    for f in folders:
        click.echo(click.style(f["name"], fg="blue"))
